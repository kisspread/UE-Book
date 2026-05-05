# Skeletal Mesh Morph Target Editing Tools

> Tools to edit morph targets within the skeletal mesh editor.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | 否（Installed: false） |
| 包含内容 | 是 |
| 模块 | SkeletalMeshMorphTargetEditingTools (Editor) |
| 创建时间 | 2025-01-14 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/SkeletalMeshMorphTargetEditingTools) | |

## 用途

在 UE5 的 Skeletal Mesh Editor（Persona）的 Modeling Mode 中提供 Morph Target 顶点雕刻工具。它解决的核心问题是：**在编辑器内直接雕刻和编辑 Morph Target 的顶点偏移**，无需借助外部 DCC 工具（如 Maya、Blender）来回导入导出。

该插件基于 UE5 的 Modeling Tools 框架，作为 SkeletalMeshModelingTools 的扩展（`ISkeletalMeshModelingModeToolExtension`）注册到 Skeletal Mesh Editor 的 Modeling Mode 中，出现在工具栏的 **Morph** 分区下。

## 使用场景

- 你已经在 Skeletal Mesh Editor 中创建了 Morph Target（例如表情 BlendShape），但需要在引擎内微调顶点位置
- 你想在编辑器中快速修复 Morph Target 中的穿模、不对称等细节问题
- 你想在特定骨骼 Pose 下雕刻 Morph Target，使其在动画姿势中看起来正确
- 你想用"擦除"笔刷快速回退某个 Morph Target 的变形效果到未变形状态

## 蓝图用法

本插件是纯编辑器工具，没有暴露 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。所有功能通过 Skeletal Mesh Editor 的 Modeling Mode UI 操作。

## C++ 用法

### 架构概览

本插件的核心类结构：

- `UMorphTargetVertexSculptToolBuilder` — 工具构建器，继承自 `UMeshVertexSculptToolBuilder`，负责检查是否有正在编辑的 Morph Target 并创建工具实例
- `UMorphTargetVertexSculptTool` — 主工具类，继承自 `UMeshVertexSculptTool`，同时实现 `ISkeletalMeshEditingInterface` 和 `IMorphTargetEditingToolInterface`
- `IMorphTargetEditingToolInterface` — Morph Target 编辑工具的公共接口，负责与 `USkeletalMeshEditorContextObjectBase` 的绑定/解绑
- `UMorphTargetEditingToolProperties` — 工具属性集，显示当前正在编辑的 Morph Target 名称
- `FEraseMorphTargetBrushOp` — 自定义笔刷操作，用于将 Morph Target 变形擦除回未变形状态

### 工具注册机制

插件通过 Modular Feature 系统注册到 Skeletal Mesh Editor：

```cpp
// SKMMorphTargetEditingToolsModule.cpp
void FSkeletalMeshMorphTargetEditingToolsModule::StartupModule()
{
    FSkeletalMeshMorphTargetEditingToolsStyle::Register();
    FSkeletalMeshMorphTargetEditingToolsCommands::Register();
    IModularFeatures::Get().RegisterModularFeature(
        ISkeletalMeshModelingModeToolExtension::GetModularFeatureName(), this);
}
```

工具在 `GetExtensionTools()` 中注册为 "Sculpt Morph Target"，并注册到 "Morph" 工具分区。

### Morph Target 雕刻核心逻辑

工具使用 `UMeshVertexSculptTool` 的顶点雕刻能力，但做了以下定制：

1. **Pose 感知雕刻**：通过 `PoseChangeDetector` 监听骨骼姿态变化，当姿态改变时动态变换雕刻网格，使用户可以在任意 Pose 下雕刻
2. **Morph Target 提取**：笔刷结束时，通过 `GetUnposedMesh()` 从雕刻结果中反向计算 Morph Target delta
3. **DynamicMesh 缓存**：使用 `ToolDynamicMesh` 缓存 Morph Target 属性数据，Apply 时批量提交到资产

### 擦除笔刷

`FEraseMorphTargetBrushOp` 实现了一个特殊的"擦除"笔刷，它将顶点向**未应用当前 Morph Target 的位置**移动，效果是逐渐抹除 Morph Target 的变形效果：

```cpp
// EraseMorphTargetBrushOps.h
virtual void ApplyStamp(const FDynamicMesh3* Mesh, const FSculptBrushStamp& Stamp,
    const TArray<int32>& Vertices, TArray<FVector3d>& NewPositionsOut) override
{
    const FDynamicMesh3* MeshWithoutCurentMorph = GetMeshWithoutCurrentMorphFunc();
    // 将顶点向无 Morph Target 的位置移动，强度受 Strength 和 Falloff 控制
    FVector3d TargetPos = MeshWithoutCurentMorph->GetVertex(VertIdx);
    FVector3d MoveVec = Normalized(TargetPos - OrigPos) * UsePower * Falloff;
    MoveVec = MoveVec.GetClampedToMaxSize(MaxDelta.Length());
    NewPositionsOut[k] = OrigPos + MoveVec;
}
```

## Demo 示例

### 在 Skeletal Mesh Editor 中使用 Morph Target Sculpt Tool

1. 打开 Skeletal Mesh Editor（双击一个 Skeletal Mesh 资产）
2. 确保启用了本插件（Edit → Plugins → 搜索 "SkeletalMeshMorphTargetEditingTools"，勾选启用，重启编辑器）
3. 在 Skeletal Mesh Editor 中切换到 **Modeling** 模式
4. 在 Morph Targets 面板中，用单选按钮选择一个要编辑的 Morph Target
5. 在工具栏的 **Morph** 分区下，点击 **Sculpt Morph Target** 按钮
6. 使用标准雕刻笔刷在网格上雕刻 Morph Target 的顶点偏移
7. 使用 **EraseSculptLayer** 符刷类型可擦除 Morph Target 变形
8. 雕刻完成后点击 **Apply** 提交更改到资产

### 关键操作说明

- **骨骼 Pose 编辑**：工具启用后会激活骨骼操控，你可以在雕刻的同时调整骨骼姿态，工具会实时更新雕刻网格
- **对称支持**：支持对称雕刻，但如果在关闭对称的情况下结束笔刷，对称将被永久禁用（直到工具重启）
- **Undo/Redo**：完整支持撤销/重做，每个笔刷 stroke 都是一个可撤销的操作

## 模块依赖

从 `Build.cs` 的依赖列表提取。如果你要扩展本插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `ModelingToolsEditorMode` | Modeling Tools 编辑器模式框架 |
| `SkeletalMeshModelingTools` | Skeletal Mesh 的 Modeling Tools 集成（插件级依赖） |
| `MeshModelingToolsEditorOnly` | Mesh Modeling Tools 的编辑器专用部分 |
| `ModelingComponents` | Modeling Tools 通用组件（如 DynamicMeshComponent） |
| `MeshConversion` | MeshDescription ↔ DynamicMesh 转换 |
| `MeshModelingTools` | Mesh Modeling Tools 核心（如 MeshVertexSculptTool） |
| `InteractiveToolsFramework` | UE5 交互式工具框架 |
| `SkeletalMeshUtilitiesCommon` | Skeletal Mesh 通用工具函数 |
| `GeometryCore` | 几何核心（FDynamicMesh3 等） |
| `SkeletalMeshModifiers` | Skeletal Mesh 修改器 |
| `MeshDescription` | MeshDescription 数据结构 |
| `SkeletalMeshDescription` | Skeletal Mesh 的 MeshDescription 扩展 |
| `Persona` | Skeletal Mesh Editor（Persona）框架 |
| `SkeletalMeshEditor` | Skeletal Mesh Editor 实现 |
| `GeometryFramework` | 几何框架（DynamicMeshActor 等） |
| `UnrealEd` | 编辑器核心 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-09 | `afd04d5` | [MorphSculptTool] 添加数组大小检查以避免处理 null stroke 时崩溃 |
| 2025-10-07 | `a75fe45` | [MorphTargetSculptTool] 修复撤销笔刷时 octree 过期的问题 |
| 2025-09-11 | `4bad7ac` | [SKMModelingTools] 支持将工具更改累积到 DynamicMesh 缓存中再批量应用到资产；重构 Morph Target 工具为 DynamicMesh 架构；新增 Morph Target Manager 面板 |

### 维护评价

- **创建时间**：2025-01-14，约 1 年历史，属于 🆕 较新的插件
- **最近更新**：2025-10-09，3 个月内有实质性功能更新和 bug 修复
- **活跃程度**：**活跃维护** — 最近一次更新包含架构重构（DynamicMesh 缓存）、新功能（Morph Target Manager）和 bug 修复
- **实验性标记**：`IsExperimentalVersion: true`，`Installed: false`，需要手动启用
- **已知限制**：仅支持单选工具；对称功能在非对称 stroke 后永久禁用
- **推荐使用**：✅ 适合在开发和测试环境中使用，用于快速编辑 Morph Target。但由于是实验性插件，生产环境使用需谨慎，建议关注后续更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/SkeletalMeshMorphTargetEditingTools)
- 依赖插件：[SkeletalMeshModelingTools](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/SkeletalMeshModelingTools)
