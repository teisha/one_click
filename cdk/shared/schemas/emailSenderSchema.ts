import { BatchWriteCommandOutput, DeleteCommandOutput, PutCommandOutput } from '@aws-sdk/lib-dynamodb';
import { EmailSender } from '../models/emailSender';
import { DynamoService } from '../services/dynamodb.service';

interface DbModel {
  PK: string;
  SK: string;
  domainPart?: string;
  deleteByDomain: boolean,
  dateAdded: string;
}

export const EMAIL_SENDERS_PK = 'EMAIL_SENDER';
export class EmailSenderSchema {
  constructor(private dynamo: DynamoService) {}

  async put(item: EmailSender): Promise<PutCommandOutput> {
    return await this.dynamo.putItem(this.convertItemToDbModel(item));
  }

  async putAll(items: EmailSender[]): Promise<BatchWriteCommandOutput> {
    return await this.dynamo.batchWrite(items.map(item => this.convertItemToDbModel(item) ))
  }

  async delete(emailAddress: string): Promise<DeleteCommandOutput> {
    const key = {
      PK: EMAIL_SENDERS_PK,
      SK: emailAddress,
    };
    const response = await this.dynamo.deleteItem(key);
    console.log('Deleted: ', { response });
    return response;
  }

  async get(emailAddress: string): Promise<EmailSender | null> {
    const key = {
      PK: EMAIL_SENDERS_PK,
      SK: emailAddress,
    };
    const response = await this.dynamo.getItem(key);
    if (!response.Item) {
      return null;
    }
    return this.convertDbModelToItem(response.Item as DbModel);
  }

  // To implement:
  // async getAll(): Promise<any> {
  //   const params = {
  //     KeyConditionExpression: 'PK = :value',
  //     ExpressionAttributeValues: {
  //       ':value': EMAIL_SENDERS_PK,
  //     },
  //   };

  //   const allAgents = await this.dynamo.query(params);
  //   allAgents.Items = allAgents.Items.map((item: DbModel) => this.convertDbModelToItem(item));
  //   return allAgents;
  // }

  convertItemToDbModel(item: EmailSender): DbModel {
    const model: DbModel = {
      PK: EMAIL_SENDERS_PK,
      SK: item.emailAddress,
      domainPart: item.domainPart,
      deleteByDomain: item.deleteByDomain, // ? 1 : 0,
      dateAdded: item.dateAdded
    };
    return model;
  }

  convertDbModelToItem(data: DbModel): EmailSender {
    const item: EmailSender = {
      emailAddress: data.SK,
      domainPart: data.domainPart,
      deleteByDomain: data.deleteByDomain, // === 0 ? false : true,
      dateAdded: data.dateAdded
    };
    return item;
  }
}
