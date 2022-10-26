import { CfnResponse } from '../model/cfnResponse';
import * as fs from 'fs';
import { S3Service } from '../services/s3Service';
import { ResourceProps } from '../model/resourceProps';
import { Context } from 'aws-lambda';
import { CfnResponseService } from '../services/cfnResponseService';
import { CfnCustomResourceBase } from './cfnCustomResourceBase';
import { getLogger } from '../services/loggingService';
import { ApiError } from '../model/apiError';

// eslint-disable-next-line @typescript-eslint/no-empty-interface
interface IProps
  extends ResourceProps<{
    BucketName: string;
    KeyPrefix: string;
    FileKey: string;
  }> {}

export class MoveConfigDataFiles extends CfnCustomResourceBase {
  constructor(context: Context, cfn: CfnResponseService, private s3: S3Service) {
    super(context, cfn, getLogger('MoveConfigDataFiles'));
  }

  validateInput(event: IProps): void {
    if (!event.ResourceProperties.BucketName) {
      throw new ApiError(400, 'BucketName is a required property');
    }
    if (!event.ResourceProperties.KeyPrefix) {
      throw new ApiError(400, 'KeyPrefix is a required property');
    }
    if (!event.ResourceProperties.FileKey) {
      throw new ApiError(400, 'FileKey is a required property');
    }
  }

  private async uploadFile(event: IProps) {
    this.logger.info('Current directory: ' + process.cwd());
    const filename = `./${event.ResourceProperties.FileKey}.json`;
    const fileJson = fs.readFileSync(filename, { encoding: 'utf-8' });

    await this.s3.putJSON(
      event.ResourceProperties.BucketName,
      `${event.ResourceProperties.KeyPrefix}/${event.ResourceProperties.FileKey}.json`,
      JSON.parse(fileJson)
    );
  }

  async create(event: IProps): Promise<CfnResponse> {
    await this.uploadFile(event);
    return {
      status: 'SUCCESS',
      message: 'Resource Created',
      data: null,
    };
  }

  async update(event: IProps): Promise<CfnResponse> {
    await this.uploadFile(event);
    return {
      status: 'SUCCESS',
      message: 'Resource Unchanged',
      data: null,
    };
  }

  async delete(): Promise<CfnResponse> {
    //do nothing on teardown
    return {
      status: 'SUCCESS',
      message: 'Nothing done for Delete',
      data: null,
    };
  }
}
