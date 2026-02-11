<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import Mdict from './Mdict/index.vue'
import DictManage from './DictManage/index.vue'

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
  <template v-else-if="route === 'mdict-manage'">
    <DictManage />
  </template>
  <template v-else>
    <div style="padding: 16px; font-size: 14px;">
      未识别的功能
    </div>
  </template>
</template>
