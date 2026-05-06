# NiagaraPreviewContent

> Contains movie files used in Niagara

| 属性 | 值 |
|---|---|
| 中文名 | Niagara预览素材 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（电影文件） |
| 模块 | `NiagaraPreviewContent` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-05 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraPreviewContent) | |

## 用途

此插件提供了一系列电影（视频）文件，专为 Niagara 视觉效果系统设计。这些视频文件可用作 Niagara 粒子系统的纹理源（例如视频纹理采样），用于在编辑器预览窗口或运行时展示动态背景、火焰、水流等效果。它的存在解决了 Niagara 使用第三方视频素材时需要手动导入的问题，提供了一套预设的、与 Niagara 流程集成度高的预览素材。

## 使用场景

- **Niagara 编辑器预览**：在创建 Niagara 发射器或系统时，直接调用这些电影文件作为贴图源，快速查看粒子与动态视频交互的效果。
- **快速原型开发**：无需外部准备视频素材，即可在项目中使用高质量的 Niagara 预览内容，加速视觉原型验证。
- **视频纹理教学**：学习 Niagara VideoTexture 或其他视频相关模块时，有现成的素材可直接使用。

## 蓝图用法

本插件仅包含电影文件资源，不暴露任何蓝图可调用函数或蓝图节点。因此，在蓝图中无法直接引用本插件的 API，但可以通过内容浏览器浏览并引用其提供的视频素材。

### 使用资源方式

1. 在内容浏览器中搜索路径 `NiagaraPreviewContent`（插件安装后会自动挂载）。
2. 将任意 `.mov` 或 `.mp4` 文件拖动到 Niagara 编辑器的“纹理”或“媒体纹理”属性中。
3. 在粒子渲染阶段的 `SetTexture` 节点中绑定该媒体纹理。

## C++ 用法

本插件不提供 C++ 公共 API（仅包含模块启动/关闭实现），因此没有可供调用的类或函数。若需要在 C++ 中加载其中的媒体文件，通过常规的 `UMediaPlayer` 和 `UMediaSource` 路径引用资源即可：

```cpp
// 通过资源路径加载媒体源
UMediaSource* MediaSource = LoadObject<UMediaSource>(nullptr, TEXT("/NiagaraPreviewContent/SampleVideo"));
```

## Demo 示例

由于插件不含任何可编程接口，无需提供独立示例。其价值在于直接在 Niagara 编辑器中使用附带视频文件。可按照以下步骤快速验证：

1. 新建一个 Niagar 发射器。
2. 在粒子渲染中加入 `RenderSprite` 模块，并将纹理设置为 `NiagaraPreviewContent` 下的一个视频文件。
3. 在 `Update` 阶段添加 `VideoPlayer` 相关的模块（如 `VideoTexture`）以驱动视频播放。

## 模块依赖

此插件为纯内容插件（附带 Editor 模块用于资源注册），不引入额外运行时依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

- 2025-05-05 [fd724ac](https://github.com/EpicGames/UnrealEngine/commit/fd724acf) — Niagara Movie Preview Assets

### 维护评价

该插件于 2025 年 5 月首次提交，仅有一个初始提交，属于全新插件。由于发布时间极短，尚无后续更新记录。预期作为内容资源包，后续维护频率可能较低，但当前状态非常稳定（内容无需频繁变更）。适合直接使用其提供的视频素材进行 Niagara 开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraPreviewContent)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraPreviewContent/Tests)（暂无测试内容）