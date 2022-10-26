import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { IOTBackendStack } from '../constructs/IOTBackendStack';

const stage = process.env.DEPLOYMENT_ENV ?? 'dev'
const app = new cdk.App();
new IOTBackendStack(app, `IOTBackendStack${stage}`, {
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.REGION
    },
    stage: stage,
});

app.synth();