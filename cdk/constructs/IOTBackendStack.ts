import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as pylambda from '@aws-cdk/aws-lambda-python-alpha'
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import path from 'path';

import { AttributeType, BillingMode, ProjectionType, StreamViewType, Table, TableAttributes } from 'aws-cdk-lib/aws-dynamodb';
// import { Role, ServicePrincipal, ManagedPolicy } from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { Effect, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { Aws, CfnOutput, Fn } from 'aws-cdk-lib';
import { Runtime } from 'aws-cdk-lib/aws-lambda';




export interface IOTBackendStackProps extends cdk.StackProps {
  stage: string;
}

// cdk bootstrap aws://001668627821/us-east-1 --profile power-user
export class IOTBackendStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: IOTBackendStackProps) {
      super(scope, id, props);

      const iotClickTable = new Table(this, 'IotClickTable', {
        tableName: 'IOTClicks_' + props.stage,
        partitionKey: {
          name: 'pk',
          type: AttributeType.STRING
        },
        sortKey: {
          name: 'sk',
          type: AttributeType.STRING
        },
        billingMode: BillingMode.PAY_PER_REQUEST,
        stream: StreamViewType.NEW_IMAGE,
        timeToLiveAttribute: 'TTL'
      });

      iotClickTable.addGlobalSecondaryIndex({
        indexName: 'GSI1',
        partitionKey: {
          name: 'sk',
          type: AttributeType.STRING
        },
        sortKey: {
          name: 'pk',
          type: AttributeType.STRING
        },
        projectionType: ProjectionType.ALL
      });
      iotClickTable.addGlobalSecondaryIndex({
        indexName: 'startIndex',
        partitionKey: {
          name: 'start',
          type: AttributeType.STRING
        },
        sortKey: {
          name: 'pk',
          type: AttributeType.STRING
        },
        projectionType: ProjectionType.ALL
      });

      cdk.Tags.of(iotClickTable).add('Environment', props.stage);
      cdk.Tags.of(iotClickTable).add('Project', 'OneClick');

      const iotClickTablePolicy = new iam.PolicyStatement({
        effect: Effect.ALLOW,
        actions: [  'dynamodb:DeleteItem','dynamodb:GetItem','dynamodb:GetRecords',
          'dynamodb:PutItem','dynamodb:UpdateItem','dynamodb:Query'],
        resources: [iotClickTable.tableArn]
      })

      const bucket = s3.Bucket.fromBucketName(this, 'SourceBucket', 'lsft-athena-investigations')

      const bucketAccessPolicy = new iam.PolicyStatement({
        effect: Effect.ALLOW,
        actions:  ['s3:GetObject', 's3:ListBucket'],
        resources: [bucket.bucketArn, Fn.join('/', [bucket.bucketArn, '*'])]
      })
      

      const hubitatParameter = new ssm.StringParameter(this, 'HubitatParameter', {
        parameterName: `/OneClick/${props.stage}/Hubitat`,
        stringValue: 'non-Secure-string' ,   // will be updated through cli to secure string after deploy
        description: 'SSM Parameter for call to IOT Manager'
      });
      const hubitatParameterPolicy = new iam.Policy(this, 'ParameterPolicy',{
        statements: [
          new iam.PolicyStatement({
            effect: Effect.ALLOW,
            actions: ['ssm:GetParameter', 'ssm:PutParameter'],
            resources: [hubitatParameter.parameterArn]

          }), 
          new iam.PolicyStatement({
            effect: Effect.ALLOW,
            actions: ['ssm:DescribeParameters'],
            resources: ["*"]
          })
        ]
      });

      cdk.Tags.of(hubitatParameter).add('Environment', props.stage);
      cdk.Tags.of(hubitatParameter).add('Project', 'OneClick');

      // Needs to be built before you can do this.
      // const clickLambda = new lambda.Function(this, 'ClickLambda', {
      //   runtime: Runtime.PYTHON_3_9,
      //   handler: 'lambda_clicker.py',
      //   code: lambda.Code.fromAsset(path.join(__dirname, '../../backend/src/services')), 
      // })
      
      // uses a docker container to build the lambda
      const clickLambda = new pylambda.PythonFunction(this, 'ClickLambda', {
        entry: '../backend/src',
        runtime: Runtime.PYTHON_3_9,
        timeout:  cdk.Duration.minutes(5),
        // index:   // needs a file named index.py
        // handler:  // defaults to handler
        environment: {
          "LOGGING_LEVEL": "INFO",
          "CLICK_TABLE": iotClickTable.tableName,
          "SECRET_PARAM": hubitatParameter.parameterName,
          "SINGLE_CLICK": "48a74731-3b5f-4acd-b7f2-1e1c707c1c39",
          "DOUBLE_CLICK": "941967c0-26cc-4b3a-a36c-99b85e2ad568",
          "HOLD": "d902d1cd-784f-4bce-b1e7-36c1dc603d9d"
        }
      })
      
      clickLambda.role?.attachInlinePolicy(
        new iam.Policy(this, 'executionRole', {
          statements: [bucketAccessPolicy, iotClickTablePolicy],
        }),
      );
      hubitatParameterPolicy.attachToRole(clickLambda.role!);



      // const logGroup = new logs.LogGroup(api, 'ApiAccessLogs', {
      //     retention: 90, // Keep logs for 90 days
      // });
      /* create an API */
      const buttonClickApiGateway = new apigw.RestApi(this, 'buttonClickApi', {
        deployOptions: {
          stageName: props.stage
        }, 
        defaultCorsPreflightOptions: {
          allowHeaders: [
            'Content-Type',
            'X-Amz-Date',
            'Authorization',
            'X-Api-Key',
          ],
          allowMethods: ['OPTIONS','GET','POST'],
          allowCredentials: true,
          allowOrigins: ['http://98.44.205.136'],
        }   
      })
// curl -L -X GET 'https://apwae7ot0f.execute-api.us-east-1.amazonaws.com/dev/buttonClick/workbutton/48a74731-3b5f-4acd-b7f2-1e1c707c1c39'
// Double
// curl -L -X GET 'https://apwae7ot0f.execute-api.us-east-1.amazonaws.com/dev/buttonClick/workbutton/941967c0-26cc-4b3a-a36c-99b85e2ad568'
// HOLD
// curl -L -X GET 'https://apwae7ot0f.execute-api.us-east-1.amazonaws.com/dev//buttonClick/workbutton/d902d1cd-784f-4bce-b1e7-36c1dc603d9d'
// {"message":"Missing Authentication Token"}
// AmazonAPIGatewayPushToCloudWatchLogs 
//
 
// aws lambda add-permission --function-name arn:aws:lambda:XXXXXX:your-lambda-function-name --source-arn arn:aws:execute-api:us-east-1:YOUR_ACCOUNT_ID:api_id/*/HTTP_METHOD/resource --principal apigateway.amazonaws.com --statement-id apigateway-access --action lambda:InvokeFunction
      clickLambda.addPermission("PermitAPIGatewayExecute", {
        principal: new ServicePrincipal("apigateway.amazonaws.com"),
        sourceArn: buttonClickApiGateway.arnForExecuteApi('*')
      })
       
      /* add a resource to the API and a method to the resource */
      const buttonClick = buttonClickApiGateway.root.addResource('buttonClick');
      buttonClick.addMethod('GET')
      const buttonType = buttonClick.addResource('{buttonType}');
      buttonType.addMethod('GET')
      const clickType = buttonType.addResource('{clickType}')
      clickType.addMethod('GET', new apigw.LambdaIntegration(clickLambda));

      
      new CfnOutput(this, 'APIGatewayURL', {value: buttonClickApiGateway.url})
      // const authorizer = new HttpLambdaAuthorizer('BooksAuthorizer', authHandler, {
      //   responseTypes: [HttpLambdaResponseType.SIMPLE], // Define if returns simple and/or iam response
      // });


    }
  }






/*

            - Effect: Allow
              Action:
                  - kms:CreateAlias
                  - kms:Decrypt
                  - kms:Encrypt
                  - kms:UpdateAlias                    
              Resource:
                - "Fn::Join":
                  - ":"
                  - - "arn:aws:kms"
                    - Ref: 'AWS::Region'
                    - Ref: 'AWS::AccountId'
                    - 'key/*'                
                - "Fn::Join":
                  - ":"
                  - - "arn:aws:kms"
                    - Ref: 'AWS::Region'
                    - Ref: 'AWS::AccountId'
                    - 'alias/*' 

*/


/*
    const lambdas: LambdaProps[] = [
      /**
       *
       * CONNECT/BACKEND LAMBDAS
       *
  
      {
        /**
         *
         * Streaming handler that calls the kinesis audio lambda
         *
     
        handler: 'invokeStreaming/index.handler',
        name: 'invoke-streaming',
        runtime: Runtime.NODEJS_12_X,
        memorySize: 1024,
        lambdaTimeout: 300,
        connectInstanceId,
        logicalIds: logicalIds?.invokeStreaming,
        environment: {
          RECORDINGS_BUCKET_NAME: this.voicemailBucket.bucketName,
          MAX_VOICEMAIL_MINUTES: maxVoicemailMinutes ?? '2'
        },
        statements: [
          new PolicyStatement({
            effect: Effect.ALLOW,
            actions: [
              'kinesisvideo:GetDataEndpoint',
              'kinesisvideo:GetMedia',
              'kinesisvideo:ListFragments',
              'kinesisvideo:GetMediaForFragmentList'
            ],
            // TODO: this needs to not be star
            resources: ['*']
          }),
          new PolicyStatement({
            effect: Effect.ALLOW,
            actions: ['s3:PutObject'],
            resources: [this.voicemailBucket.bucketArn, Fn.join('/', [this.voicemailBucket.bucketArn, '*'])]
          }),
          new PolicyStatement({
            effect: Effect.ALLOW,
            actions: ['lambda:InvokeFunction'],
            resources: [`arn:aws:lambda:${region}:${this.account}:function:${prefix}-invoke-streaming`]
          })
        ],
        ...vpcProps
      },
      {
        /**
         *
         * After kvs function turns raw file into .wav it saves
         * the file back to the bucket.  This handler listens for
         * that event and inserts the database entry for the ui
         *
    
        handler: 'putVoicemailToDB/index.handler',
        name: logicalIds ? 'put-vm-to-db-v3' : 'put-vm-to-db',
        table: 'voicemail-table',
        environment: {
          TRANSCRIPT_ENABLE: transcribeEnabled ? 'enabled' : 'disabled',
          TTL_IN_SECONDS: `${expiration ? expiration.toSeconds() : -1}`
        },
        events: [
          new S3EventSource(this.voicemailBucket, {
            events: [EventType.OBJECT_CREATED],
            filters: [{suffix: transcribeEnabled ? '.json' : '.wav'}]
          })
        ],
        statements: [
          new PolicyStatement({
            effect: Effect.ALLOW,
            actions: ['s3:GetObject', 's3:ListBucket'],
            resources: [this.voicemailBucket.bucketArn, Fn.join('/', [this.voicemailBucket.bucketArn, '*'])]
          })
        ],
        ...vpcProps
      },
      {
        /**
         *
         * Once the voicemail recorded is inserted into dynamo,
         * this handler will listen to the stream for that event
         * and send an email notification
         *
         
        handler: 'sendEmailNotification/index.handler',
        name: logicalIds ? 'send-email-notification-v3' : 'send-email-notification',
        table: 'voicemail-table',
        environment: {
          REPLY_EMAIL: replyEmail,
          WEBAPP_URL: webDomain,
          ADD_WAV_ATTACHMENT: addWavAttachment,
          VOICEMAIL_BUCKET: this.voicemailBucket.bucketName
        },
        events: [
          new DynamoEventSource(tables.resources['voicemail-table'], {
            batchSize: 10,
            retryAttempts: 3,
            enabled: true,
            startingPosition: StartingPosition.TRIM_HORIZON
          })
        ],
        statements: [
          new PolicyStatement({
            effect: Effect.ALLOW,
            actions: ['ses:SendEmail', 'ses:SendRawEmail'],
            // eslint-disable-next-line no-template-curly-in-string
            resources: [Fn.sub('arn:aws:ses:${AWS::Region}:${AWS::AccountId}:identity/*')]
          }),
          new PolicyStatement({
            effect: Effect.ALLOW,
            actions: ['s3:GetObject', 's3:ListBucket'],
            resources: [this.voicemailBucket.bucketArn, Fn.join('/', [this.voicemailBucket.bucketArn, '*'])]
          })
        ],
        ...vpcProps
      },
*/



/*
 ConnectTable:
    Type: "AWS::DynamoDB::Table"
    DeletionPolicy: Retain
    Properties:
      TableName: !Sub "${Client}-${Project}-${Environment}-connect-table"
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: ext
          AttributeType: S  
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE
      BillingMode: PAY_PER_REQUEST
      GlobalSecondaryIndexes:
        - IndexName: skIndex
          KeySchema:
            - AttributeName: SK
              KeyType: HASH
            - AttributeName: PK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL  
        - IndexName: extIndex
          KeySchema:
            - AttributeName: ext
              KeyType: HASH
            - AttributeName: PK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL   

  CcpApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub "${Client}-${Project}-ccp-api-${Environment}"
      Description: Provides server-side code to ccp-wrapper
      CodeUri: .
      Handler: src/api/index.ccpApiLambda
      Policies:
        - AWSLambdaRole
        - Statement:
            - Sid: updateAttributes
              Effect: Allow
              Action:
                - connect:UpdateContactAttributes
              Resource: !Sub arn:aws:connect:${AWS::Region}:${AWS::AccountId}:instance/${ConnectInstanceId}/contact/*
            - Effect: Allow
              Action:
                - "dynamodb:Query"
                - "dynamodb:PutItem"
                - "dynamodb:GetItem"
                - "dynamodb:BatchGetItem"
                - "dynamodb:UpdateItem"
                - "dynamodb:DeleteItem"               
              Resource:
                - "Fn::GetAtt":
                    - ConnectTable
                    - Arn
                - "Fn::Join":
                    - /
                    - - "Fn::GetAtt":
                          - ConnectTable
                          - Arn
                      - index
                      - typeIndex       

                        LambdaFunctionPolicy:
    Type: 'AWS::IAM::Policy'
    Properties:
      PolicyName: !Sub 'plcy_${Client}-${Project}-${Environment}-lambda'
      PolicyDocument:
        Statement:
          - Effect: Allow
            Action:
              - logs:CreateLogGroup
              - logs:CreateLogStream
              - logs:DescribeLogStreams
              - logs:PutLogEvents
            Resource: !Sub 'arn:aws:logs:${AWS::Region}:${AWS::AccountId}:*'
          - Effect: Allow
            Action:
              - dynamodb:Scan
              - dynamodb:Query
              - dynamodb:UpdateItem
              - dynamodb:DeleteItem
              - dynamodb:GetItem
              - dynamodb:PutItem
            Resource: 
              - !GetAtt ConnectTable.Arn
              - Fn::Join:
                - ""
                - - Fn::GetAtt: [ConnectTable, Arn]
                  - "/*"
      Roles:
        - !Ref LambdaFunctionRole  
        - !Ref LexIntentFullfillmentFunctionRole  
*/
