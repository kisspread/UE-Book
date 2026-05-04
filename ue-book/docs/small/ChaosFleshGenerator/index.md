# Chaos Flesh Generator

> Chaos Flesh Data Generator for ML Deformer

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | — |
| 包含内容 | true |
| 模块 | ChaosFleshGenerator (Editor) |
| 创建时间 | 2024-03-13 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/ChaosFleshGenerator) | |

## 用途

ChaosFleshGenerator 是一个 Editor-only 插件，用于 **批量生成 Chaos Flesh（软体/肉体）物理模拟训练数据**，并将结果输出为 GeometryCache，供 ML Deformer 框架消费。

ML Deformer 需要大量"骨骼姿态 → 顶点位移"的配对数据来训练神经网络变形器。手动生成这些数据既繁琐又不可重复。ChaosFleshGenerator 的存在就是自动化这个流程：给定一个 Chaos Flesh Asset、一个骨骼网格体和一段动画序列，它会在后台逐帧驱动 Chaos 物理求解器进行软体模拟，收集每帧的模拟顶点位置，最终写入 GeometryCache 资产。

插件深度依赖 ChaosFlesh（软体物理）、GeometryCache 和 MLDeformerFramework 三大模块，是 ML Deformer 生态中面向肉体/软体变形场景的数据生产工具。

## 使用场景

- 你正在使用 ML Deformer 训练一个 **肌肉/肉体层次的变形器**（而非布料），需要为 ChaosFlesh 求解器生成训练数据
- 你已有一个导入的 SkeletalMesh（FBX 导入，有 MeshToImportVertexMap）和对应的 FleshAsset，想要自动化地对动画序列跑物理模拟并导出 GeometryCache
- 你需要对模拟参数（帧率、子步数、迭代次数等）进行精确控制，以获得高质量的训练数据

## 编辑器用法

### 入口

插件在 ML Deformer 编辑器的 **Tools 菜单** 中添加了一个 **"Chaos Flesh Generator"** 菜单项。打开方式：

1. 打开 ML Deformer Asset 的编辑器
2. 在工具栏找到 **Tools** 菜单
3. 点击 **Chaos Flesh Generator**，会弹出一个专用的 Generator Tab

### Generator Tab 面板

面板由两部分组成：

**属性面板（Details View）** — 显示 `UFleshGeneratorProperties` 的所有属性：

#### Input（输入）

| 属性 | 类型 | 说明 |
|---|---|---|
| `SkeletalMeshAsset` | USkinnedAsset* | 用于 ML Deformer 的骨骼网格体，**必须是 FBX 导入的原始网格体**（需要 MeshToImportVertexMap） |
| `FleshAsset` | UFleshAsset* | Chaos Flesh 资产，其 SkeletalMesh 必须与上方的 SkeletalMeshAsset 一致 |
| `AnimationSequence` | UAnimSequence* | 训练姿态动画序列 |
| `FramesToSimulate` | FString | 帧范围字符串，如 `"0, 2, 5-10, 12-15"`。留空则模拟所有帧 |

#### Output（输出）

| 属性 | 类型 | 说明 |
|---|---|---|
| `SimulatedCache` | UGeometryCache* | 输出的 GeometryCache 资产，面板旁有 **"New"** 按钮可快速创建 |

#### SimulationSettings（模拟设置）

| 属性 | 默认值 | 说明 |
|---|---|---|
| `FrameRate` | 24 | 训练动画帧率（TimeStep = 1/FrameRate） |
| `NumFrames` | 150 | 模拟帧数（动画长度） |
| `NumSubSteps` | 2 | 每个时间步的子步细分数（SolverStep = TimeStep/NumSubSteps） |
| `NumIterations` | 5 | 约束求解器每步的收敛迭代次数 |
| `SolverEvolution` | — | 演化参数组 |
| `SolverCollisions` | — | 碰撞参数组 |
| `SolverConstraints` | — | 约束参数组 |
| `SolverForces` | — | 力参数组 |
| `SolverDebugging` | — | 调试参数组 |

**"Start Generating" 按钮** — 点击后开始后台模拟。进度以 `FAsyncTaskNotification` 弹窗显示，支持取消。

### 典型工作流

1. 准备好 SkeletalMesh（FBX 导入）、FleshAsset、AnimSequence
2. 创建或指定一个 GeometryCache 作为输出
3. 在 ML Deformer 编辑器中打开 Chaos Flesh Generator Tab
4. 配置输入资产和模拟参数
5. 点击 **Start Generating**
6. 等待进度条完成，GeometryCache 自动保存

### 重要约束

- SkeletalMeshAsset **必须** 是 FBX 导入的（有 MeshToImportVertexMap），程序化生成的网格体不支持
- SkeletalMesh 只能有 **1 个 Section**，多 Section 会报错
- FleshAsset 的 SkeletalMesh 属性必须与指定的 SkeletalMeshAsset 完全一致
- 模拟期间无法启动新的生成任务

## 蓝图用法

此插件为 Editor-only 模块，不提供 BlueprintCallable 函数。所有操作通过 ML Deformer 编辑器 UI 完成。

## C++ 用法

此插件的所有类都在 `Private` 目录下，没有 Public API，不设计为外部 C++ 模块调用。以下是内部架构说明。

### 核心架构

```
FChaosFleshGenerator (FTickableEditorObject)
  ├── UFleshGeneratorProperties (UObject, 持有所有参数)
  ├── FTaskResource (异步任务资源管理)
  │     ├── FAsyncTask<TTaskRunner<FLaunchSimsTask>> (后台任务)
  │     ├── FAsyncTaskNotification (进度通知)
  │     └── SimResources[] (模拟资源数组)
  └── FLaunchSimsTask (实际模拟逻辑)
        └── 逐帧 Simulate(): Pose → WriteToSimulation → Simulate → ReadFromSimulation
```

### 关键类

| 类 | 职责 |
|---|---|
| `FChaosFleshGenerator` | 编辑器 Tick 对象，驱动整个生成流程（StartGenerate → TickGenerate） |
| `UFleshGeneratorProperties` | 持有所有输入/输出/模拟参数，作为 UI 与逻辑之间的数据桥梁 |
| `FTaskResource` | 管理异步任务生命周期：创建临时 Editor World、Spawn Actor 和 Component、分配/释放资源 |
| `FLaunchSimsTask` | 后台线程执行的模拟任务，逐帧驱动 Chaos 求解器 |
| `UFleshGeneratorComponent` | 继承自 UFleshComponent，添加 Pose 功能 |
| `USkeletalGeneratorComponent` | 继承自 USkeletalMeshComponent，为离线模拟服务 |
| `SFleshGeneratorWidget` | Slate UI 面板，展示属性和 Start 按钮 |
| `FChaosFleshGeneratorToolsMenuExtender` | 注册到 ML Deformer 编辑器 Tools 菜单的扩展器 |

### 模拟流程（从源码解读）

```cpp
// 1. 验证所有输入资产的有效性
// 2. 获取 MeshToImportVertexMap（FBX 导入顶点映射）
// 3. 解析 FramesToSimulate 字符串
// 4. 创建临时 Editor World，Spawn Actor，创建 Component：
//    - UFleshGeneratorComponent (Flesh 组件)
//    - USkeletalGeneratorComponent (骨骼网格体组件)  
//    - UDeformableSolverComponent (变形求解器)
// 5. 配置求解器参数（帧率、子步、迭代等）
// 6. 启动后台 FAsyncTask
// 7. 后台逐帧循环：
//    a. GetBoneTransforms() — 从 AnimSequence 提取骨骼变换
//    b. FleshComponent.Pose() — 将骨骼变换应用到 Flesh
//    c. SolverComponent.WriteToSimulation() → Simulate() → ReadFromSimulation()
//    d. GetRenderPositions() — 从 FleshCollection 提取表面顶点位置
// 8. 完成后 SaveGeometryCache() 写入资产
```

## 模块依赖

从 Build.cs 的 PublicDependencyModuleNames 和 PrivateDependencyModuleNames 提取。

### Public Dependencies

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `ChaosCore` | Chaos 物理核心 |
| `Chaos` | Chaos 物理框架 |

### Private Dependencies

| 模块 | 用途 |
|---|---|
| `CoreUObject` | UObject 系统 |
| `ChaosFlesh` | Chaos 软体物理资产与组件（FleshAsset、FleshComponent） |
| `ChaosFleshEngine` | Chaos Flesh 引擎层支持 |
| `ChaosFleshNodes` | Chaos Flesh 节点系统 |
| `DataflowCore` | Dataflow 核心框架 |
| `DataflowEditor` | Dataflow 编辑器支持 |
| `DataflowEngine` | Dataflow 引擎层 |
| `DataflowSimulation` | Dataflow 模拟框架（含 DataflowSimulationGeometryCache） |
| `Engine` | UE 引擎核心 |
| `GeometryCache` | GeometryCache 资产系统（输出格式） |
| `MLDeformerFramework` | ML Deformer 运行时框架 |
| `MLDeformerFrameworkEditor` | ML Deformer 编辑器框架（Tools 菜单扩展点） |
| `PropertyEditor` | 属性面板系统 |
| `RenderCore` | 渲染核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器功能 |

### 插件依赖（.uplugin）

| 插件 | 说明 |
|---|---|
| `ChaosFlesh` | Chaos 软体物理插件 |
| `GeometryCache` | 几何缓存插件 |
| `MLDeformerFramework` | ML Deformer 框架插件 |

## 维护状态

### 近期更新

| 日期 | Commit | 内容 | 解读 |
|---|---|---|---|
| 2025-09-23 | `0e93909a64a3` | ChaosFlesh: 修复 GT/PT collection 更新通过 solver proxy（改为 shared ptr）、修复 deformable solver proxy 删除、添加 flesh asset collection 变更时的组件传播 | 修复了求解器代理生命周期和集合更新的核心 bug，属于重要的底层修复 |
| 2025-04-11 | `43d8b16087de` | Fix include for module manager | 编译修复，小改动 |
| 2025-02-26 | `1eb5b0f5a6fa` | Chaosflesh: 修复 geometry cache 帧率（默认 24，现改为使用 simulation fps） | 修复了输出 GeometryCache 帧率不正确的 bug |

### 维护评价

- **创建时间**：2024-03-13（约 2 年前）
- **最近更新**：2025-09-23（约 7 个月前）
- **维护状态**：**维护中** — 近一年内有功能性更新和 bug 修复
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion: true`，说明 Epic 仍将其视为实验性功能
- **代码质量**：源码结构清晰，职责分离合理（Generator / Simulation / Threading / UI 各司其职），但所有源文件都在 Private 目录下，没有 Public API
- **已知限制**：
  - 只支持单线程模拟（`NumThreads = 1` 硬编码）
  - 要求 SkeletalMesh 只有 1 个 Section
  - 要求 FBX 导入的网格体（依赖 MeshToImportVertexMap）
  - 不支持 Flesh LOD
- **推荐度**：如果你在使用 ChaosFlesh + ML Deformer 的工作流，这是唯一的自动化数据生成工具，值得使用。但需注意其实验性状态和上述限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/ChaosFleshGenerator)
- 官方文档：无（DocsURL 为空）
- [MLDeformerFramework 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformerFramework)（父级框架）
