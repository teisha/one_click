import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { beforeEach, describe, it } from '@jest/globals';
import { DynamoService } from '../../shared/services/dynamodb.service';
import { S3Service } from '../../shared/services/s3.service';
import { connectDynamo, connectS3, setupEnvironment } from '../testUtils';
import { ImportEmailsToDynamo } from '../../sender_uploader/ImportEmailsToDynamo'

// npm run backend:test -- cdk/tests/sender_uploader/ImportEmailsToDynamo.test.ts
describe('ImportEmailsToDynamo handler', () => {
    let dynamodb: DynamoDBClient;
    let dynamoService: DynamoService;
    let s3Service: S3Service;
    beforeEach(() => {
        setupEnvironment();
        dynamodb = connectDynamo();
        dynamoService = new DynamoService('MailSort_dev', dynamodb);
        s3Service = new S3Service(connectS3());
    })

    it('reads the file and adds the emails to the table', async () => {
        const lambda = new ImportEmailsToDynamo(dynamoService, s3Service);
        await lambda.handler({from: 'test'});
    }, 800000) 
})