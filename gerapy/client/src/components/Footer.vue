<template>
	<div>
		<footer class="footer" v-once>Copyright &copy; {{ getYear }} 百达智慧 All Rights Reserved.
		</footer>
	</div>
</template>
<script>
	export default {
		computed: {
			getYear() {
				return new Date().getFullYear()
			}
		}
	}
</script>
