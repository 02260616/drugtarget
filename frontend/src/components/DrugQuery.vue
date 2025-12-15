<template>
  <div class="container">
    <h2 class="title">🧬 药物靶点智能分析</h2>

    <!-- 输入区 -->
    <div class="search-box">
      <input
        v-model="drug"
        placeholder="请输入药物名称（如 Aspirin）"
        class="input"
      />
      <button @click="query" class="btn" :disabled="loading">
        {{ loading ? "查询中..." : "查询" }}
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      🔍 正在分析药物靶点，请稍候…
    </div>

    <!-- 结果区 -->
    <div v-if="result" class="result">

      <!-- 靶点 -->
      <h3 class="section-title">🎯 预测靶点（Predicted Targets）</h3>
      <table class="table">
        <thead>
          <tr>
            <th>靶点</th>
            <th>置信度</th>
            <th>DrugBank</th>
            <th>药敏（GDSC）</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in result.targets" :key="'t' + index">
            <td>{{ item.Target }}</td>
            <td>{{ item.Confidence }}</td>
            <td>{{ item.DrugBank ? "✔" : "✘" }}</td>
            <td>{{ item.GDSC ? "✔" : "✘" }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 基因 -->
      <h3 class="section-title">🧬 相关基因（Related Genes）</h3>
      <table class="table">
        <thead>
          <tr>
            <th>基因</th>
            <th>置信度</th>
            <th>DrugBank</th>
            <th>药敏（GDSC）</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in result.genes" :key="'g' + index">
            <td>{{ item.Gene }}</td>
            <td>{{ item.Confidence }}</td>
            <td>{{ item.DrugBank ? "✔" : "✘" }}</td>
            <td>{{ item.GDSC ? "✔" : "✘" }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 通路 -->
      <h3 class="section-title">🛣️ 相关通路（Related Pathways）</h3>
      <table class="table">
        <thead>
          <tr>
            <th>通路</th>
            <th>置信度</th>
            <th>DrugBank</th>
            <th>药敏（GDSC）</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in result.pathways" :key="'p' + index">
            <td>{{ item.Pathway }}</td>
            <td>{{ item.Confidence }}</td>
            <td>{{ item.DrugBank ? "✔" : "✘" }}</td>
            <td>{{ item.GDSC ? "✔" : "✘" }}</td>
          </tr>
        </tbody>
      </table>

    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api";

const drug = ref("");
const result = ref(null);
const loading = ref(false);

const query = async () => {
  loading.value = true;
  result.value = null;

  try {
    const res = await api.post("/query_drug", {
      drug_name: drug.value
    });
    result.value = res.data;
  } catch (e) {
    alert("查询失败，请检查后端是否已启动。");
  }

  loading.value = false;
};
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 40px auto;
  padding: 30px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
}

.title {
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
}

.search-box {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 25px;
}

.input {
  width: 320px;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #dcdcdc;
  font-size: 14px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  background: #409eff;
  color: #fff;
  cursor: pointer;
}

.btn:disabled {
  background: #a0cfff;
}

.loading {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.result {
  margin-top: 30px;
}

.section-title {
  margin: 30px 0 10px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  background: #fafafa;
}

.table th,
.table td {
  padding: 10px;
  border-top: 1px solid #eaeaea;
}
</style>
