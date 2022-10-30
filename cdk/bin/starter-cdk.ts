import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { CdkStarterStack } from '../constructs/cdk-starter-stack';

// "deploy:practiceApi": "REGION=us-east-1 DEPLOYMENT_ENV=dev npx aws-cdk deploy"
//REGION=us-east-1 DEPLOYMENT_ENV=dev  npx aws-cdk deploy --app='ts-node bin/starter-cdk.ts' --outputs-file ./cdk-outputs.json
//npx ts-node --prefer-ts-exts bin/cdk.ts

const stage = process.env.DEPLOYMENT_ENV ?? 'dev'
const app = new cdk.App();
new CdkStarterStack(app, `CdkApiStarterStack${stage}`, {
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.REGION
    },
});

app.synth();