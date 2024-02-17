const { setupDCP, Worker } = require('@distributive/custom-worker');
const axios = require('axios');
const process = require('process');

const dcp = setupDCP();

class BlenderWorker extends Worker {

	constructor(watchDog) {
		super(watchDog, [{ name: 'custom:blender', versions: ['0.0.0'] }]);
		debugger;
	};

	async run(jobId, slice, sliceDatum, code)
	{
		const port = process.env['PORT'] || "8001";
		const blendFile = new Uint8Array(Buffer.from(code, 'base64'));

		const startTime = process.hrtime.bigint();
		const resp = await axios.post(
			`http://localhost:${port}/render/${sliceDatum}`,
			blendFile 
		);
		const diffTime = Number( process.hrtime.bigint() - startTime ) / 1e6;

		const data = resp.data;
		const result =	Buffer.from(data, 'base64');


		return {
			result: result,
			metrics: {
				CPUDensity: 1.,
				GPUDensity: 1.,
				CPUTime: diffTime,
				GPUTime: diffTime,
				InDataSize: blendFile.length,
				OutDataSize: result.length,
			}
		};
	};
	
	async postRequest()
	{
		let newSliceCount = 0;
		for (const jobId in this.jobs) {
			newSliceCount += Object.keys( this.jobs[jobId].slices ).length;
		};
		if (newSliceCount > 0)
			console.log(`Pulled ${newSliceCount} slices to compute.`);
		debugger;
	};
}




async function main() 
{
	const worker = new BlenderWorker(1000);

	let failCount = 0;
	while (true)
	{
		try{
			await worker.connectToTaskDistributor();
			failCount = 0;
			await worker.loop();
		} catch(err) {
			console.error(err);
			const delay = 10 * 2 ** failCount * 1000;
			console.log(`Try again in ${delay/1000} seconds`);
			await new Promise((res)=>{ setTimeout(res, delay) }); 
		}
	}
};



main().then(()=>{
	console.log("Done");
	process.exit(0);
}).catch((err)=>{
	console.error(err);
	process.exit(1);
});
