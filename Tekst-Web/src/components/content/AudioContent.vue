<script setup lang="ts">
import type { AudioResourceRead } from '@/api';
import AudioPlayer from '@/components/AudioPlayer.vue';
import { NFlex } from 'naive-ui';
import { onBeforeUpdate, ref, type CSSProperties } from 'vue';
import CommonContentDisplay from './CommonContentDisplay.vue';

const props = withDefaults(
  defineProps<{
    resource: AudioResourceRead;
    focusView?: boolean;
    showComments?: boolean;
  }>(),
  {
    focusView: false,
  }
);

const playerRefs = ref<{ id: string; ref: InstanceType<typeof AudioPlayer> }[]>([]);

const fontStyle: CSSProperties = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-ui)',
};

function handlePlay(playerInstanceId: string) {
  playerRefs.value.forEach((p) => {
    if (p.id !== playerInstanceId) {
      p.ref.pause();
    }
  });
}

function handleEnded(playerInstanceId: string) {
  const index = playerRefs.value.findIndex((p) => p.id === playerInstanceId);
  if (index !== -1 && index < playerRefs.value.length - 1) {
    playerRefs.value[index + 1].ref.play(true);
  }
}

onBeforeUpdate(() => {
  playerRefs.value = [];
});
</script>

<template>
  <div>
    <common-content-display
      v-for="content in resource.contents"
      :key="content.id"
      :show-comments="showComments"
      :authors-comment="content.authorsComment"
      :editors-comment="content.editorsComment"
      :font="fontStyle.fontFamily"
    >
      <n-flex :vertical="!focusView" size="large">
        <audio-player
          v-for="(file, fileIndex) in content.files"
          :ref="
            (el) =>
              el &&
              playerRefs.push({
                id: `player-${content.id}-${fileIndex}`,
                ref: el as InstanceType<typeof AudioPlayer>,
              })
          "
          :key="fileIndex"
          :src="file.url"
          :external-link="file.sourceUrl || undefined"
          :compact="focusView"
          :caption="file.caption || undefined"
          :font-style="fontStyle"
          @play="() => handlePlay(`player-${content.id}-${fileIndex}`)"
          @ended="() => handleEnded(`player-${content.id}-${fileIndex}`)"
        />
      </n-flex>
    </common-content-display>
  </div>
</template>
