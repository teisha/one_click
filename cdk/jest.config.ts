import type {JestConfigWithTsJest} from 'ts-jest/dist/types';
import baseJest from '../jest.config';

const config: JestConfigWithTsJest = {
  ...baseJest
};

export default config;
