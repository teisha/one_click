// from vf-softphone


const cfn = new CfnResponseService();



/*

*/

const moveConfigDataFiles = async (
  event: CloudFormationCustomResourceEvent,
  context: Context
): Promise<CfnResponse> => {
  const s3 = new S3Service();
  const lambda = new MoveConfigDataFiles(context, cfn, s3);
  return await lambda.handler(event);
};

export const handler = async (event: CloudFormationCustomResourceEvent, context: Context): Promise<CfnResponse> => {
  // eslint-disable-next-line no-console
  console.log(event);
  if (event.ResourceType === 'Custom::DeployFrontEnd') {
    return await deployFrontEnd(event, context);
  } else if (event.ResourceType === 'Custom::AssociateLambdaFunction') {
    return await associateLambda(event, context);
  } else if (event.ResourceType === 'Custom::AssociateApprovedOrigin') {
    return await associateApprovedOrigin(event, context);
  } else if (event.ResourceType === 'Custom::MoveConfigDataFiles') {
    return await moveConfigDataFiles(event, context);
  } else {
    await cfn.failed(event, context, `Unknown Custom Resource Type: ${event.ResourceType} / ${event.RequestType}`);
  }
};



//

import { CloudFormationCustomResourceEvent, Context } from 'aws-lambda';
import axios from 'axios';
import { CfnResponse } from '../model/cfnResponse';
import { getLogger } from './loggingService';

export class CfnResponseService {
  private logger = getLogger('CfnResponseService');

  async success(event: CloudFormationCustomResourceEvent, context: Context, data: unknown): Promise<void> {
    return await this.sendResponse(event, context, {
      status: 'SUCCESS',
      message: `See the details in CloudWatch Log Stream: ${context.logStreamName}`,
      data,
    });
  }

  async failed(event: CloudFormationCustomResourceEvent, context: Context, message: string): Promise<void> {
    return await this.sendResponse(event, context, {
      status: 'SUCCESS',
      message,
      data: null,
    });
  }

  // Send response to the pre-signed S3 URL
  async sendResponse(
    event: CloudFormationCustomResourceEvent,
    context: Context,
    cfnResponse: CfnResponse
  ): Promise<void> {
    this.logger.info('Sending response ' + cfnResponse.status);

    const body = JSON.stringify({
      Status: cfnResponse.status,
      Reason: cfnResponse.message,
      PhysicalResourceId: event.RequestType === 'Create' ? context.logStreamName : event.PhysicalResourceId,
      StackId: event.StackId,
      RequestId: event.RequestId,
      LogicalResourceId: event.LogicalResourceId,
      Data: cfnResponse.data,
    });

    this.logger.info('RESPONSE BODY', { body });

    const response = await axios.put(event.ResponseURL, body);

    this.logger.info('CloudFormation Response:', { response });
    return;
  }
}