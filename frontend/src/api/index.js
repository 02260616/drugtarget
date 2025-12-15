import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:8000",  // 后端地址
  timeout: 2000000
});

export default instance;
