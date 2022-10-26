

// lsft-athena-investigations/

import { EmailSender } from '../shared/models/emailSender';
import { EmailSenderSchema } from '../shared/schemas/emailSenderSchema';
import { DynamoService } from '../shared/services/dynamodb.service';
import { S3Service } from '../shared/services/s3.service';

export class ImportEmailsToDynamo {
    private schema: EmailSenderSchema;
    constructor(private dynamo: DynamoService, private s3: S3Service) {
        this.schema = new EmailSenderSchema(dynamo)
    }

    public async handler(event: unknown): Promise<void> {
        console.log(JSON.stringify(event, null, 2));

        const bucket = process.env.BUCKET ?? '';
        const key = process.env.EMAIL_FILE_KEY ?? '';
        // const bucket = 'lsft-athena-investigations';
        // const key = 'mailSort/emails_consolidated.txt'

        console.log('GET FILE FROM ' + bucket + ' // ' + key)
        const result = await this.s3.get(bucket, key);
        if (result && result !== '') {
            const emailList = result.split('\n')
            // await this.schema.putAll(emailList.map(email => ({
            //         emailAddress: email,
            //         deleteByDomain: false,
            //         dateAdded: new Date().toISOString()                
            // })))
            for (const email of emailList) {

                const record: EmailSender = {
                    emailAddress: email,
                    deleteByDomain: false,
                    dateAdded: new Date().toISOString()
                }
                await this.schema.put(record);
            }
        }



    }
  
}