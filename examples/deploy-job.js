#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

async function main() {
  const compute = require('dcp/compute');
  const wallet = require('dcp/wallet');

  function range(size, startAt = 0) {
      return [...Array(size).keys()].map(i => i + startAt);
  }

  const frames = range(240, 1);

  const blendFileName = path.join(__dirname, 'BlackHole-Blender.blend')
  const blendFile = fs.readFileSync(blendFileName).toString('base64');

  const job = compute.for(frames, blendFile);

  job.worktime = 'custom:blender'
  job.customWorktime = true;

  job.greedyEstimation = true;

  job.on('accepted', () => {
    console.log(job.id);
  });
  job.on('readystatechange', console.log);
  job.on('result', (event) => {
    console.log(event);
    const sliceNumber = event.sliceNumber;
    const result = event.result;
    fs.writeFileSync(`./out/${sliceNumber}.png`, result);
  });
  job.on('console', console.log);

  job.public.name = `blender~worktime~${new Date().toLocaleTimeString()}`;

  let results = await job.exec();

  for (let i=0; i < results.length; i++) {
    console.log(frames[i]);
    console.log(results[i].length);
    fs.writeFileSync(`./out/${frames[i]}.png`, results[i]);
  };
}

require('dcp-client')
  .init()
  .then(main)
