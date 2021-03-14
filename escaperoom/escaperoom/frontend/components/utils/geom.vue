<script>
import {mapState} from 'vuex'
import RootElement from './root'

export default {

  components: {
    RootElement
  },

	data() {
		return {
		}
	},

	computed: {
    "geom.width": function() {
      return this.root.offsetWidth;
    },
    "geom.height": function() {
      return this.root.offsetHeight;
    },
    "geom.top": function() {
      return this.root.offsetTop;
    },
    "geom.right": function() {
      return this.geom.left + this.geom.width;
    },
    "geom.bottom": function() {
      return this.geom.top + this.geom.height;
    },
    "geom.left": function() {
      return this.root.offsetLeft;
    },
	},

	watch: {
	},

	methods: {
	},
}
</script>
