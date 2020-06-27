import * as tf from '@tensorflow/tfjs';
import {loadGraphModel} from '@tensorflow/tfjs-converter';

const MODEL_URL = './jestnet/model.json';

const model = await loadGraphModel(MODEL_URL);