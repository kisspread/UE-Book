# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 互换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `InterchangeAnalytics` (Runtime), `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 2021-09-01 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange) | |

## 用途

Interchange Framework 是 UE5 的新一代资产导入/导出框架，旨在取代旧的 FBX Import 系统。它提供了一个**模块化、可扩展的中间表示层**，将 3D 文件格式（FBX、glTF、USD 等）的数据转换为统一的节点图结构，然后再由工厂（Factory）将这些节点转换为实际的 UE 资产。

**核心设计理念**：
- **解耦**：解析器（Parser/Translator）只负责将文件格式转换为节点，工厂（Factory）只负责从节点创建资产
- **可扩展**：通过添加新的 Parser 支持更多文件格式，通过自定义 Pipeline 控制导入/导出行为
- **数据驱动**：所有资产属性都存储在节点的属性系统中，支持序列化和撤销

## 使用场景

- 你需要导入 FBX/glTF/USD 格式的 3D 模型、动画、材质 → 使用默认的 Interchange 导入
- 你需要自定义导入行为（如自动设置 LOD、修改材质参数） → 创建自定义 Pipeline
- 你需要支持新的 3D 文件格式 → 实现自定义 Translator/Parser
- 你需要批量导出资产到特定格式 → 使用 Interchange 导出系统
- 你需要在运行时动态加载 3D 资产 → 使用 Interchange 的运行时导入功能

## 蓝图用法

InterchangeNodes 模块主要提供数据节点的定义，蓝图中通常通过 Pipeline 和设置类来使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCustomLocalTransform` | 设置场景节点的本地变换 | `UInterchangeSceneNode` |
| `GetCustomGlobalTransform` | 获取场景节点的全局变换 | `UInterchangeSceneNode` |
| `SetPayLoadKey` | 设置网格/纹理的负载键（指向实际数据） | `UInterchangeMeshNode` / `UInterchangeTextureNode` |
| `SetSlotMaterialDependencyUid` | 设置插槽的材质依赖 | `UInterchangeSceneNode` / `UInterchangeMeshNode` |
| `SetCustomShaderType` | 设置着色器类型 | `UInterchangeShaderNode` |
| `ConnectDefaultOuputToInput` | 连接着色器节点的输入 | `UInterchangeShaderPortsAPI` |
| `SetCustomAnimationPayloadKey` | 设置动画负载键 | `UInterchangeAnimationTrackNode` |
| `SetCustomLightColor` | 设置灯光颜色 | `UInterchangeBaseLightNode` |
| `SetCustomFocalLength` | 设置相机焦距 | `UInterchangePhysicalCameraNode` |

### 使用示例（蓝图描述）

在自定义 Pipeline 中处理导入的节点图：
1. 获取 `UInterchangeBaseNodeContainer` 中的所有节点
2. 遍历 `UInterchangeSceneNode` 获取场景层级
3. 通过 `GetCustomAssetInstanceUid` 检查节点实例化了哪个资产
4. 使用 `GetSlotMaterialDependencies` 获取材质分配
5. 根据需要修改节点属性（如设置 LOD、调整变换）

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeSceneNode.h"
#include "InterchangeMeshNode.h"
#include "InterchangeMaterialDefinitions.h"
#include "InterchangeShaderGraphNode.h"
#include "InterchangeBaseNodeContainer.h"
```

### 基本用法

创建和配置场景节点：

```cpp
// 创建节点容器
UInterchangeBaseNodeContainer* NodeContainer = NewObject<UInterchangeBaseNodeContainer>();

// 创建场景节点
UInterchangeSceneNode* SceneNode = NewObject<UInterchangeSceneNode>(NodeContainer);
NodeContainer->AddNode(SceneNode);

// 设置本地变换
FTransform LocalTransform(FRotator(0, 90, 0), FVector(100, 0, 0));
SceneNode->SetCustomLocalTransform(NodeContainer, LocalTransform);

// 设置可见性
SceneNode->SetCustomComponentVisibility(true);
SceneNode->SetCustomActorVisibility(true);
```

### 进阶用法

处理网格节点和材质依赖：

```cpp
// 创建网格节点
UInterchangeMeshNode* MeshNode = NewObject<UInterchangeMeshNode>(NodeContainer);
NodeContainer->AddNode(MeshNode);

// 设置网格负载键
MeshNode->SetPayLoadKey("mesh_payload_001", EInterchangeMeshPayLoadType::STATIC);

// 设置网格属性
MeshNode->SetCustomVertexCount(1000);
MeshNode->SetCustomPolygonCount(500);
MeshNode->SetCustomHasVertexNormal(true);
MeshNode->SetCustomHasVertexTangent(true);
MeshNode->SetCustomUVCount(1);

// 设置材质槽依赖
MeshNode->SetSlotMaterialDependencyUid("MaterialSlot0", "MaterialNode_001");

// 将网格关联到场景节点
SceneNode->SetCustomAssetInstanceUid(MeshNode->GetUniqueID());
```

处理着色器图：

```cpp
// 创建着色器图节点
UInterchangeShaderGraphNode* ShaderGraph = UInterchangeShaderGraphNode::Create(NodeContainer, TEXT("MyMaterial"));

// 设置材质属性
ShaderGraph->SetCustomTwoSided(false);
ShaderGraph->SetCustomBlendMode(BLEND_Opaque);

// 添加输入值
ShaderGraph->AddLinearColorInput(TEXT("BaseColor"), FLinearColor(1, 0, 0));
ShaderGraph->AddFloatInput(TEXT("Roughness"), 0.5f);

// 连接纹理节点到着色器输入
UInterchangeShaderPortsAPI::ConnectDefaultOuputToInput(
    ShaderGraph, 
    TEXT("BaseColor"), 
    TextureNodeUid
);
```

## 模块依赖

InterchangeNodes 模块是节点定义的核心，其他模块依赖它来构建节点图。

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 核心基础类和接口 |
| `InterchangeCommon` | 通用定义和工具 |
| `InterchangeImport` | 导入系统实现 |
| `InterchangeExport` | 导出系统实现 |
| `InterchangeFactoryNodes` | 工厂节点（用于创建实际资产） |
| `InterchangePipelines` | 导入/导出管线 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | USD 预生成：实现骨骼和物理资产的跟踪 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 的本地化警告 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 重导入时重置现有 LOD 模型以更新骨骼绑定 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 恢复 uFBX 解析器为实验性功能 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects | 修复导入对象列表中空指针导致的崩溃 |

### 维护评价

**活跃维护中** ✅

Interchange Framework 是 Epic Games 重点维护的项目，作为 FBX Import 系统的官方替代方案。最近的提交显示：
- 持续修复 bug 和改进稳定性
- 积极支持新的 UE 版本（5.8）
- 正在扩展 USD 支持
- FBX 解析器仍在活跃开发

**推荐使用**：对于新项目，强烈推荐使用 Interchange 而非旧的 FBX Importer。对于已有项目，可以在新资产导入时逐步迁移到 Interchange。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/interchange-framework-in-unreal-engine/)