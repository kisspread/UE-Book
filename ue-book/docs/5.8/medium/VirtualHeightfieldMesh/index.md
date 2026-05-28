# Virtual Heightfield Mesh

> Mesh renderer for virtual texture heightfields

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟高度场网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、示例资源） |
| 模块 | `VirtualHeightfieldMesh` (Runtime), `VirtualHeightfieldMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh) | |

## 用途

Virtual Heightfield Mesh 是一个专门用于渲染虚拟纹理高度场的网格渲染器。它结合了虚拟纹理（Virtual Texture）技术和程序化网格生成，允许引擎根据相机距离动态调整高度场几何体的细分级别（LOD），实现大规模地形的高效渲染。

该插件解决了传统静态网格地形在大世界场景中面临的内存和渲染性能瓶颈——通过将高度数据存储为虚拟纹理，并动态生成适当精度的网格，可以在极低的内存占用下呈现高细节地形。

**注意**：该插件默认未启用（`EnabledByDefault=false`），且标记为实验性（`IsExperimentalVersion=true`），不适合用于生产环境。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `VirtualHeightfieldMesh` | Runtime | 核心运行时模块，负责虚拟高度场的网格生成、LOD 管理及渲染 |
| `VirtualHeightfieldMeshEditor` | Editor | 编辑器模块，提供高度场组件的编辑器集成、可视化调试工具和属性面板 |

详细 API 请参阅各子模块文档：[VirtualHeightfieldMesh](VirtualHeightfieldMesh.md) | [VirtualHeightfieldMeshEditor](VirtualHeightfieldMeshEditor.md)

## 使用场景

- 你有一个大型开放世界游戏需要渲染广阔地形 → 用 Virtual Heightfield Mesh 实现低内存占用的地形渲染
- 你需要基于虚拟纹理的地形 LOD 自动调度 → 该插件自动根据相机距离调整网格细分
- 你在进行地形渲染技术的原型验证 → 作为实验性功能进行评估测试
- 你已有虚拟纹理高度场数据 → 可直接利用该插件进行网格化渲染

## 模块依赖

该插件无特殊依赖（仅标准 Core/Engine/Slate 等），但需要启用虚拟纹理支持（`r.VirtualTextures=1`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 新日志宏 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质翻译器相关工作 |
| 2026-02-03 | `61433296` | Rename FViewMatrices members to follow the <Source>To<Target> pattern for transforms, to reduce ambi | 重命名 FViewMatrices 成员以统一变换命名规范 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧版 GPU 性能分析器相关宏 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 迁移 RHI 纹理创建调用至命令列表方式 |

### 维护评价

该插件创建于 2020 年 10 月，已有约 5 年历史。从近期提交记录来看，所有更新均为引擎全局性重构（日志宏迁移、材质翻译器、FViewMatrices 重命名、GPU Profiler 废弃、RHI API 迁移），**没有任何功能性更新或 bug 修复**。

该插件始终处于实验性状态（`IsExperimentalVersion=true`），从未从 Experimental 目录毕业。近期维护仅随引擎主干被动更新，无主动开发迹象。

⚠️ **警告**：该插件标记为实验性且默认未启用，过去 1 年内无实质性功能更新。不建议在生产项目中依赖此插件，仅适合技术评估和实验用途。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualHeightfieldMesh)
- [官方文档]()（无）