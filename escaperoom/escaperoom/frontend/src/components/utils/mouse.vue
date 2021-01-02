<script>
import {mapState} from 'vuex'

export default {

  components: {
  },

	data() {
		return {
		}
	},

	computed: {
		...mapState(['drag', 'mouse']),
	},

	watch: {
	},

	methods: {

    dragStart(e) {
      this.$store.commit('dragstart', {ref: this, x: e.clientX, y: e.clientY});
    },

	},
}
</script>
