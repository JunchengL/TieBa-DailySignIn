<div align="center">
<h1 align="center">
TieBa-DailySignIn
</h1>
</div>

![Github Actions BaiduTieBa-DailySignIn](https://github.com/JunchengL/TieBa-DailySignIn/workflows/Github%20Actions%20BaiduTieBa-DailySignIn/badge.svg)

## 工具简介


使用Github Action的百度贴吧每日签到

**如果喜欢这个项目请帮我点个 Star 吧 ✰✰✰**

## API 参考列表

- [srcrs/TiebaSignIn](https://github.com/srcrs/TiebaSignIn)

## 功能列表

* [x] 北京时间上午 9 点 10分自动开始贴吧签到任务。
* [x] 签到结果推送到Server酱

## 使用说明

### Github Actions

1. **Fork 本项目**
2. **获取 BDUSS**
- 电脑浏览器打开并登录 [百度贴吧](https://tieba.baidu.com/)
- 按 F12 打开 「开发者工具」 找到 Application -> Storage -> Cookies
- 找到 `BDUSS`，并复制值，在下一步里创建对应的 GitHub Secrets。


3. **点击项目 Settings -> Secrets -> New Secrets 添加以下 2 个 Secrets，其中server酱微信推送的sckey可参阅[微信订阅通知](http://sc.ftqq.com/?c=code)**

| Name          | Value               |
| ------------- | ------------------- |
| BDUSS         | 从 Cookie 中获取     |
| SCKEY         | server酱推送的sckey  |


4. **开启 Github Actions 并触发每日自动执行**
