# ML Deformer Framework

> Machine Learning Mesh Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 机器学习变形器框架 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MLDeformerFramework` (Runtime), `MLDeformerFrameworkEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework) | |

## 用途

ML Deformer Framework 是一个基于机器学习的网格变形框架。它通过训练 ML 模型来学习蒙皮网格的变形规则，从而在运行时以极低的性能开销实现高质量的变形效果（如肌肉隆起、布料褶皱、LOD 修正等），替代昂贵的实时物理模拟。

该框架提供可扩展的基类，支持不同类型的 ML 变形器实现。核心流程为：在离线阶段使用训练数据（高精度与低精度 mesh 对）训练模型，然后在运行时由推理后端（如 NNE）执行推理，将预测的顶点偏移应用到骨骼网格体上。

## 使用场景

- 你需要让角色有逼真的肌肉变形效果，但不想使用昂贵的实时物理模拟
- 你希望用 LOD0 的高质量动画数据训练模型，然后在低 LOD 上也能获得接近的效果
- 你需要一个可扩展的框架来集成自定义 ML 变形器方案
- 你在做电影级品质的角色动画，需要帧精确的 ML 变形驱动

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [MLDeformerFramework](MLDeformerFramework.md) | Runtime | 核心运行时框架，包含变形器基类、训练数据管理、推理集成和渲染器接口 |
| [MLDeformerFrameworkEditor](MLDeformerFrameworkEditor.md) | Runtime | 编辑器工具集，包含资产编辑器、UI 面板、Debug 可视化和 Sequencer 集成 |

> 详细 API 请参阅各子模块文档。

## 蓝图用法

核心运行时功能主要通过 C++ 扩展，蓝图层面提供 Debug 调试开关：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDebugDrawEnabled` | 启用/禁用 ML 变形器的调试可视化 | `UMLDeformerComponent` |

## C++ 用法

### 头文件引入

```cpp
#include "MLDeformerComponent.h"
#include "MLDeformerModel.h"
#include "MLDeformerAsset.h"
```

### 基本用法

```cpp
// 在角色组件上启用 ML 变形器的调试绘制
UMLDeformerComponent* DeformerComp = Actor->FindComponentByClass<UMLDeformerComponent>();
if (DeformerComp)
{
    DeformerComp->SetDebugDrawEnabled(true);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NeuralNetworkEngine` | ML 推理后端，执行训练模型的前向推理 |
| `OptimusCore` | Deformer Graph 集成，支持自定义变形计算图 |
| `GeometryCore` / `MeshConversion` | 几何处理与网格数据转换 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 5.8 版本动画废弃清理，移除过时 API |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 简化视图支持相关改动 |
| 2026-04-06 | `3f81d395` | [ContentBrowser] New Add Menu Animation Menu | 内容浏览器动画菜单重构适配 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | Deformer Graph 运行时多项修复 |

### 维护评价

**✅ 活跃维护中**

该插件于 2022 年 9 月从 Experimental 迁出，处于 **活跃维护** 状态。最近一次更新（2026-04-22）涉及 UE 5.8 的废弃清理，表明 Epic 持续对其进行工程维护。作为 Epic 官方主推的 ML 动画功能之一，该框架有完善的文档支持和持续的更新投入，**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework/Tests)