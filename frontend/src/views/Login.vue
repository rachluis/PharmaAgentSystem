<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>Pharma Agent Login</span>
        </div>
      </template>
      <el-form :model="form" label-width="0">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="Username"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="Password"
            prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="w-100" @click="handleLogin"
            >Login</el-button
          >
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { User, Lock } from "@element-plus/icons-vue";

const router = useRouter();
const form = reactive({
  username: "admin",
  password: "",
});

const handleLogin = () => {
  // Mock login
  localStorage.setItem("token", "mock-token");
  router.push("/dashboard");
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
}
.login-card {
  width: 350px;
}
.w-100 {
  width: 100%;
}
.card-header {
  text-align: center;
  font-weight: bold;
}
</style>
