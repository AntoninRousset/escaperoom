<template>
  <path :d="path"/>
</template>

<script>
import {mapState} from 'vuex'

export default {

	name: 'ETransition',
  mixins: [],
  props: {
    'i': {
      type: Number,
    },
    'points': {
      type: Array,
      default: [],
    },
  },
  emits: [],

  created() {
    console.log(this.points);
  },

  computed: {
    path() {
      let points = this.points.map(p => `${p.x} ${p.y}`)
      return 'M ' + points.join(' L ')
    },
  }

}
</script>

<style lang="scss">
	@import "../../scss/colors.scss";

  path {
    fill: none;
    stroke: #000000;
    stroke-width: 3;
 }
</style>
