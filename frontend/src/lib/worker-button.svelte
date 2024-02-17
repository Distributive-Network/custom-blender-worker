<script lang="ts">
    import { StartWorker, KillWorker } from "$lib/wailsjs/go/main/App.js";
    import { StateEnum } from "$lib/custom-types.js";


    export let state: StateEnum = StateEnum.READY;
    $: buttonText = (state == StateEnum.READY ? "Start" : state == StateEnum.RUNNING ? "Stop" : "...");
    $: buttonEnabled = (state == StateEnum.READY || state == StateEnum.RUNNING);


    async function onClickHandler() {
        switch(state) {
            case StateEnum.READY:
                state = StateEnum.RUNNING;
                await StartWorker();
                break;
            case StateEnum.RUNNING:
                state = StateEnum.CANCELLED;
                await KillWorker();
                state = StateEnum.READY;
            case StateEnum.CANCELLED:
                throw new Error("Clicked button during cancellation. Should not be possible.");
                break;
            default:
                console.error("Unknown state: ", state);
                state = StateEnum.READY;
                break
        }
        return;
    }
</script>

<div class="flex justify-center items-center">
    <button type="button" class="btn variant-filled" on:click={onClickHandler} disabled={!buttonEnabled}>{buttonText}</button>
</div>
