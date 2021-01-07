<template>
  <div id="app">
    <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
    <kwic/>
  </div>
</template>

<script>
import kwic from './components/kwic.vue'

export default {
  name: 'app',
  components: {
    kwic
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
html {
  scroll-behavior: smooth !important;
}
</style>
