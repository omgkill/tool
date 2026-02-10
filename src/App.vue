<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import Hello from './Hello/index.vue'
import Read from './Read/index.vue'
import Write from './Write/index.vue'
import Mdict from './Mdict/index.vue'

const route = ref('')
const enterAction = ref({})

onMounted(() => {
  window.utools.onPluginEnter((action) => {
    route.value = action.code
    enterAction.value = action
  })
  window.utools.onPluginOut((isKill) => {
    route.value = ''
  })
})
</script>

<template>
  <template v-if="route === 'mdict'">
    <Mdict :enterAction="enterAction" />
  </template>
  <template v-else-if="route === 'hello'">
    <Hello :enterAction="enterAction" />
  </template>
  <template v-else-if="route === 'read'">
    <Read :enterAction="enterAction" />
  </template>
  <template v-else-if="route === 'write'">
    <Write :enterAction="enterAction" />
  </template>
  <template v-else>
    <div style="padding: 16px; font-size: 14px;">
      未识别的功能 code：{{ route || '（空）' }}
    </div>
  </template>
</template>
