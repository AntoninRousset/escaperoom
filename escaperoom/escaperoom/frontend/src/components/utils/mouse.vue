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
		...mapState(['drag']),
	},

	watch: {
	},

	methods: {

    dragStart(e) {
      this.$store.commit('dragStart', {x: e.clientX, y: e.clientY});
    },

	},
}
</script>
