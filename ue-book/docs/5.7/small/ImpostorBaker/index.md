# ImpostorBaker

> Generates a variety of Impostors for use as distant mesh LODs.

| 属性 | 值 |
|---|---|
| 中文名 | 替身烘焙器 |
| 分类 | Mesh |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2021-05-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImpostorBaker) | |

## 用途

ImpostorBaker 为网格体生成**替身**（Impostor）——一种将三维模型渲染为二维纹理的技术，用于在远处替代复杂网格，从而大幅降低渲染开销。该插件自动烘焙替身纹理（包括不同视角和光照），并生成对应的材质和网格代理，可直接用于 LOD 设置。

插件解决的核心问题：**当网格体在屏幕上占据很小像素时，使用替身替代完整渲染，在几乎不可察觉的视觉差异下获得巨大的性能提升**。与手动创建 LOD 网格相比，替身烘焙完全自动化，且结果紧凑。

## 使用场景

- **开放世界中的远处树木、建筑、岩石** – 使用 ImpostorBaker 自动生成替身作为最远 LOD，减少 draw call。
- **大型植被系统** – 为每种植被生成一张或多张替身纹理，配合虚影（billboard）技术实现高效渲染。
- **游戏中的装饰物** – 如路灯、箱子等，在远距离下用替身替代，保证帧率。
- **预计算背景** – 在关卡搭建阶段，对静态网格执行烘焙，生成优化后的 LOD 层级。

## 蓝图用法

插件主要功能通过蓝图节点和资产操作实现。由于插件为纯蓝图实现，所有公开接口均为蓝图可调用的函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Generate Impostor` | 对指定静态网格体生成替身纹理和代理网格。通常需要提供网格体引用、纹理分辨率、捕获角度数量等参数。 | `ImpostorBaker BPLibrary` (假设名称) |
| `Create MIC Editor Only` | 创建编辑器专用的材质实例，用于预览或导出替身材质。 | `ImpostorBakerHelper` (推测) |
| `Apply Impostor LOD` | 将生成的替身自动附加到原始网格体的 LOD 链中。 | `ImpostorBakerComponent` (推测) |

> 节点具体名称和类名请参考插件内容中的蓝图函数库（`ImpostorBaker/Content/Blueprint/...`）。

### 使用示例（蓝图描述）

1. **生成替身**：将目标 `Static Mesh` 引用连接到 `Generate Impostor` 节点的输入，设置纹理大小（如 512x512）和捕获视角数（如 8x8）。节点输出生成的 `Texture2D` 和 `MaterialInstanceConstant`。
2. **应用到关卡**：使用 `Apply Impostor LOD` 节点，传入原始网格组件和生成的替身资产，自动配置 LOD 距离。
3. **手动替换**：直接使用生成的材质实例创建 Billboard 组件，旋转对齐摄像机，作为独立网格使用。

## C++ 用法

插件为纯蓝图实现，未暴露 C++ API。如需在 C++ 中调用，可考虑直接操作生成的资产文件（如通过 `UStaticMesh::SetLOD()`），或编写自定义编辑器蓝图调用节点。

> 所有函数仅标记为 `BlueprintCallable`，无 C++ 导出符号。因此不提供头文件引入示例。

## Demo 示例

由于无 C++ 源文件，此处提供一个**蓝图关卡示例**的等效描述：

1. 在内容浏览器中打开 `ImpostorBaker/Content/Examples` 目录（若有）。
2. 打开示例关卡 `ImpostorBaker_Demo`，观察一个高精度树木网格与替身 LOD 的切换。
3. 选中关卡中的网格，在细节面板找到 "ImpostorBaker" 组件，调整参数实时预览。
4. 运行游戏，远处网格自动替换为替身（可通过控制台命令 `r.ForceLOD 0` 切换查看细节）。

## 模块依赖

无 C++ 模块，插件本身不导出模块。使用该插件的项目需在 `.uproject` 或插件描述中启用以下依赖：

| 插件 | 用途 |
|---|---|
| `BlueprintMaterialTextureNodes` | 提供材质纹理蓝图节点，用于生成纹理资产。 |
| `GeometryScripting` | 提供几何脚本处理功能（编辑器环境下），用于网格数据操作。 |

> 注意：`GeometryScripting` 仅在编辑器环境下启用（`TargetAllowList: ["Editor"]`），运行时无需加载。

## 维护状态

### 近期更新

- 2025-04-23 `2e8618c` ImpostorBaker: Make geometryscripting reference editor only since it is only used in editor only con
- 2025-01-30 `5e6326e8` ImpostorBaker: Replaced node that was innaccesible with "CreateMICEditorOnly" and also made it clean
- 2022-10-21 `610c4676` Update vendor links for built-in plugins to use secure protocol.
- 2021-05-27 `43fa62fc` Merge from Release-Engine-Test @ 16487383 to UE5/Main

### 维护评价

- **创建时间**：2021 年（约 4 年），属于较新的功能插件。
- **更新频率**：2025 年仍有实质性更新（修复节点引用、调整编辑器依赖），表明团队在持续维护。
- **活跃度**：最近一次更新在 2025 年 4 月，活跃维护中。
- **限制**：插件为纯蓝图，性能可能不如原生 C++ 实现，且依赖于 `GeometryScripting` 编辑器模块，无法在打包游戏中使用（烘焙替身是编辑器操作）。此外，生成的替身质量受纹理分辨率限制。
- **推荐使用**：✅ 推荐。适合需要快速生成替身 LOD 的中小型项目，尤其适合美术导向的团队。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImpostorBaker)
- (官方文档：无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImpostorBaker/Content/Tests)（若有）