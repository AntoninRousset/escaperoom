<template>
	<div class="fsm" v-if="fsm">
    <e-statemachine-editor
      :states="fsm.states"
      :transitions="fsm.transitions"
      />
	</div>
</template>

<script>
import 'normalize.css'
import {mapState} from 'vuex'
import EStatemachineEditor from './components/statemachine/editor.vue'

export default {

	components: {
		EStatemachineEditor
	},

	data() {
		return {
		}
	},

	created() {
		this.$store.commit('fetch_fsm');
	},

	computed: mapState(['fsm']),

  mounted() {

    window.addEventListener('mouseup', (e) => {
      this.$store.commit('dragEnd', {x: e.clientX, y: e.clientY});
    });

    window.addEventListener('mousemove', (e) => {
      this.$store.commit('mouseMove', {x: e.clientX, y: e.clientY});
    });

  },
}
</script>

<style lang="scss">
	@import "@icon/themify-icons/themify-icons.css";
	@import "./scss/colors.scss";
</style>
