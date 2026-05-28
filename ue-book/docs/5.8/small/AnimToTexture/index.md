# AnimToTexture

> Converts SkeletalMesh Animations into Textures

| 属性 | 值 |
|---|---|
| 中文名 | 动画转纹理 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `AnimToTexture` (Runtime), `AnimToTextureEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-03-09 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AnimToTexture) | |

## 用途

将骨骼网格体（Skeletal Mesh）的动画数据烘焙到纹理中，使得在运行时可以通过采样纹理驱动顶点动画，从而替代骨骼动画系统。核心解决的问题是：**大量角色同时播放动画时的性能瓶颈**。

通过将骨骼动画转换为顶点位置纹理，可以在材质中读取 UV 坐标对应的顶点位移，实现 GPU 驱动的实例化动画，极大减少骨骼计算的 CPU 开销。

## 使用场景

- 你需要在场景中同时渲染数百甚至数千个带动画的角色（如 RTS 大军、人群系统）→ 用 AnimToTexture 将动画烘焙到纹理，配合 Instanced Static Mesh 实现高性能实例化动画
- 你需要将骨骼动画资产转为静态网格体顶点动画以用于 Niagara 粒子系统 → 用 AnimToTexture 导出顶点位移纹理
- 你有复杂的骨骼动画但希望在低端设备上用更轻量的方式播放 → 烘焙纹理后仅需采样即可驱动动画

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| `AnimToTexture` | Runtime | 核心运行时模块，提供动画烘焙到纹理的数据资产（`UAnimToTextureDataAsset`）及材质函数 |
| `AnimToTextureEditor` | Editor | 编辑器模块，提供烘焙操作的编辑器工具和 UI |

## 相关链接

- [AnimToTexture 模块文档](AnimToTexture.md)
- [AnimToTextureEditor 模块文档](AnimToTextureEditor.md)
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AnimToTexture)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 UE_LOGF |
| 2025-10-07 | `dcc26116` | Fixed up plugins that have both Base and Default ini files, and one plugin (WebSocketNetworking) t | 修复插件配置文件兼容性问题 |
| 2025-08-08 | `7213adb2` | [AnimToTexture] Added SkeletalMesh MeshDescription functions. (not used) | 新增骨骼网格体 MeshDescription 相关函数（暂未使用） |
| 2025-08-07 | `1aee06f6` | [AnimToTexture] Fixed Baking RigidBodies | 修复刚体骨骼动画烘焙的 Bug |
| 2025-08-06 | `785cdd6d` | Fixup API macro usage | 修正 API 导出宏使用方式 |

### 维护评价

- **状态**: 维护中，2025 年 8 月有实质性功能更新（刚体烘焙修复、MeshDescription 扩展）
- 仍处于 **Experimental** 状态，尚未正式发布
- 从 2023 年创建至今持续有更新，由 Epic Games 官方维护
- 近期更新集中在 Bug 修复和底层代码完善，表明功能已趋于稳定
- **推荐使用**: 如果你有大量实例化动画的需求，值得尝试，但需注意实验性 API 可能在未来版本发生变化