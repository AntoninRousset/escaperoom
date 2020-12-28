<template>
  <path :d="'M ' + x0 + ' ' + y0 + ' L ' + x1 + ' ' + y1" />
</template>

<script>
import {mapState} from 'vuex'

export default {

  components: {
  },

	name: 'ETransition',
  mixins: [],
	props: ['src', 'dest'],
  emits: ['unselectAll'],

	data() {
		return {
      gridStep: 20,
		}
	},

  created() {
  },

	computed: {

    x0() {
      return (src.x + 1) * this.gridStep;
    },
    
    y0() {
      return (src.y + 1) * this.gridStep;
    },

    x1() {
      return (dest.x + 1) * this.gridStep;
    },

    y1() {
      return (dest.x + 1) * this.gridStep;
    },

  },

	watch: {
	},

	methods: {
	},
}
</script>

<style lang="scss">
	@import "../../scss/colors.scss";

  path {
    stroke: #000000;
    stroke-width: 3px;
 }
</style>
