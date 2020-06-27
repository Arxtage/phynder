import 'babel-polyfill';
import * as tf from '@tensorflow/tfjs';
import {JestNet} from './jestnet';
import imageURL from './cat.jpg';

const cat = document.getElementById('cat');
cat.onload = async () => {
  const resultElement = document.getElementById('result');

  resultElement.innerText = 'Loading JestNet...';

  const jestNet = new JestNet();
  console.time('Loading of model');
  await jestNet.load();
  console.timeEnd('Loading of model');

  const pixels = tf.browser.fromPixels(cat);

  console.time('First prediction');
  let result = jestNet.predict(pixels);
  const topK = jestNet.getTopKClasses(result, 5);
  console.timeEnd('First prediction');

  resultElement.innerText = '';
  topK.forEach(x => {
    resultElement.innerText += `${x.value.toFixed(3)}: ${x.label}\n`;
  });

  console.time('Subsequent predictions');
  result = jestNet.predict(pixels);
  jestNet.getTopKClasses(result, 5);
  console.timeEnd('Subsequent predictions');

  jestNet.dispose();
};
cat.src = imageURL;