# Post Process Material Chain Graph

> Post Process Material Chain Graph allows users to stack post process materials and render those into render targets separate from Scene Color.  
> This can operate on textures other than scene color without writing those into scene color.

| 属性 | 值 |
|---|---|
| 中文名 | 后处理材质链图 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `PPMChainGraph` (Runtime), `PPMChainGraphEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PostProcessMaterialChainGraph) | |

---

## 总体用途

该插件解决了传统后处理链只能修改 Scene Color 的限制。它允许用户**创建材质链图（Chain Graph）**，将多个后处理材质堆叠在一起，并将最终结果输出到独立的 Render Target 中（不受 Scene Color 影响）。这样，开发者可以在不污染主场景颜色的前提下，对任意纹理（如自定义通道、光照贴图等）施加后处理效果，或构建独立的后处理管线（如风格化特效、调试视图）。

**核心优势**：
- 后处理材质可脱离 Scene Color 独立运行。
- 支持多个材质串联/并联，形成复杂的后处理拓扑。
- 输出渲染目标可由用户自由指定，便于后续合成或复用。

---

## 模块列表

| 模块 | 类型 | 一句话总结 | 文档 |
|---|---|---|---|
| `PPMChainGraph` | Runtime | 运行时核心：定义材质链图资产、节点和渲染逻辑 | [PPMChainGraph.md](PPMChainGraph.md) |
| `PPMChainGraphEditor` | Editor | 编辑器支持：自定义资产编辑器、节点图编辑 UI、资源工厂 | [PPMChainGraphEditor.md](PPMChainGraphEditor.md) |

---

## 使用场景

- **风格化渲染**：在场景色彩叠加之前，对分离的纹理（如 AO、粗糙度、自定义着色）施加后处理，再与主场景合成。
- **调试工具**：将特定后处理效果渲染到独立视口，不影响主游戏画面。
- **多层特效**：需要多道后处理按特定顺序/条件执行，且效果不应互相干扰。
- **自定义合成管线**：例如将深度、法线等缓冲区先做处理，然后用于后期调色或 Stencil 效果。

---

## 相关链接

- [源码 (5.7)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PostProcessMaterialChainGraph)
- [官方文档]()（该插件暂无独立官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PostProcessMaterialChainGraph/Tests)（若存在）