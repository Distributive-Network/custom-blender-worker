<script lang="ts">
	import DCPLogo from '$lib/distributive-logo.svelte';
	import { StateEnum } from '$lib/custom-types';
	import WorkerButton from '$lib/worker-button.svelte';
	import { ProgressBar } from '@skeletonlabs/skeleton';

	let progress: number | undefined = undefined;
	let workerState = StateEnum.READY;
</script>

<div class="container h-screen mx-auto flex justify-center items-center">
	<div class="space-y-5">
		<h1 class="h1 center"><DCPLogo /></h1>
		<h3 class="h3 center">Render with Distributive</h3>
		{#if workerState != StateEnum.READY}
			<div class="w-full space-y-4">
				<ProgressBar meter="h-2 bg-surface-500-600-token" value={progress} total=100/>
			</div>
		{/if}
		<WorkerButton bind:state={workerState}/>
	</div>
</div>
