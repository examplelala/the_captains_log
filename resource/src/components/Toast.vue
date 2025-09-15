<template>
  <div
    v-if="message"
    class="toast"
    @click="$emit('close')"
  >
    {{ message }}
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

defineProps({
  message: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close'])

onMounted(() => {
  setTimeout(() => {
    emit('close')
  }, 3000)
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: var(--cool-gradient);
  color: white;
  padding: 16px 24px;
  border-radius: 12px;
  font-size: 0.9em;
  font-weight: 500;
  z-index: 2000;
  cursor: pointer;
  animation: toastSlide 0.3s ease, toastFade 0.3s ease 2.7s;
  box-shadow: var(--shadow-strong);
}

@keyframes toastSlide {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes toastFade {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}
</style>