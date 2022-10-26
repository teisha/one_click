import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { S3Client } from '@aws-sdk/client-s3';
import { DynamoService } from '../shared/services/dynamodb.service';
import { S3Service } from '../shared/services/s3.service';
import { ImportEmailsToDynamo } from './ImportEmailsToDynamo';

    // process.env.profile = 'power-user';
    // process.env.REGION = 'us-east-1';
    // process.env.BUCKET = 'lsft-athena-investigations';
    // process.env.EMAIL_FILE_KEY = 'mailSort/emails_consolidated.txt'   

export const upload = async (event: unknown) : Promise<void> => {
    const mailSortTable = process.env.TABLE_NAME ?? '';
    const dynamodb: DynamoDBClient = new DynamoDBClient({
        region: process.env.REGION
    });
    const mailSortService: DynamoService = new DynamoService(mailSortTable, dynamodb);
    const s3Service: S3Service = new S3Service(new S3Client({region: process.env.REGION}))

    const lambda = new ImportEmailsToDynamo(mailSortService, s3Service);
    await lambda.handler(event);
} 
