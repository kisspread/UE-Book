# GeometryCacheLevelSequenceBaker

> Bake Skeletal Meshes in Level Sequence to Geometry Cache

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存序列烘焙器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器扩展） |
| 模块 | `GeometryCacheLevelSequenceBaker` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCacheLevelSequenceBaker) | |

## 用途

该插件解决的核心问题是：**将关卡序列（Level Sequence）中驱动的骨骼网格体动画，烘焙成一个静态的几何缓存（Geometry Cache）资产。**

其存在意义在于优化运行时性能。当骨骼网格体动画复杂、角色众多或目标平台性能有限时，实时计算骨骼动画可能成为瓶颈。通过将动画结果预计算并存储为一系列几何帧，可以将播放成本从 CPU 骨骼计算转移到 GPU 几何缓存读取，从而提升帧率。此功能是作为编辑器工具（通过关卡序列编辑器的扩展菜单触发）实现的，而非运行时蓝图API。

## 使用场景

-   **优化复杂角色动画**：你有一段包含大量骨骼和复杂物理模拟的过场动画，在目标平台上播放卡顿。可以使用此插件将该动画段烘焙成几何缓存，后续播放时直接使用缓存，大幅降低运行时开销。
-   **创建几何缓存资产**：你需要为某个角色的特定动作序列创建一个独立的几何缓存资产，用于在特效、LOD 或其他系统中复用。

## 蓝图用法

此插件**不提供任何公开的蓝图API或节点**。它的所有功能都通过关卡序列编辑器（Sequencer Editor）的扩展菜单来访问，是一个纯粹的编辑器工具。

## C++ 用法

该插件的 C++ API 主要为内部模块和编辑器扩展设计。其核心功能（烘焙操作）被封装为 `FGeometryCacheLevelSequenceBaker` 类的静态方法，并由编辑器UI调用。使用者通常不直接调用 C++ API，而是通过编辑器界面操作。

### 头文件引入

```cpp
// 该插件的核心类为私有，通常不建议在项目代码中直接包含。
// 如果确实需要了解内部结构，可参考：
#include "GeometryCacheLevelSequenceBaker/Public/GeometryCacheLevelSequenceBakerModule.h"
```

### 基本用法（编辑器扩展触发）

在编辑器中，烘焙功能的入口是关卡序列编辑器“动作（Actions）”菜单中新增的“Bake Geometry Cache”选项。其背后调用的核心逻辑如下（从源码 `FGeometryCacheLevelSequenceBaker` 提炼）：

```cpp
// 伪代码：展示烘焙过程的主要步骤
// 来源：Source/.../Private/GeometryCacheLevelSequenceBaker.cpp (根据头文件推断)

// 1. 从当前激活的 Sequencer 获取数据
TSharedRef<ISequencer> Sequencer = /* ... 获取当前 Sequencer 实例 ... */;

// 2. 检查并获取需要烘焙的绑定点 (Bindings) 和资产路径
TArray<FGuid> Bindings = FGeometryCacheLevelSequenceBaker::GetBindingsToBake(Sequencer);
FString PackageName, AssetName;
if (FGeometryCacheLevelSequenceBaker::GetGeometryCacheAssetPathFromUser(PackageName, AssetName))
{
    // 3. 调用核心烘焙函数
    FGeometryCacheLevelSequenceBaker::Bake(Sequencer);
}
```

### 进阶用法（内部状态管理）

从头文件可以看出，烘焙过程是分阶段的 (`EStage`)，并封装了多个作用域（Scope）来临时修改引擎和组件设置，烘焙完成后自动恢复。这确保了烘焙过程的环境一致性和对场景状态的最小侵入。

```cpp
// 进阶概念：烘焙过程的状态机与作用域
// 来源：Source/.../Private/GeometryCacheLevelSequenceBaker.h

// 烘焙任务内部定义了阶段
enum class EStage
{
    Gather,           // 收集每帧的几何和材质数据
    RequestReadback,  // 发起GPU数据回读请求
    WriteToAsset,     // 将收集的数据写入 GeometryCache 资产
    End               // 结束
};

// 使用作用域对象临时覆盖设置（例如）
// FSkeletalMeshComponentSettingScope - 临时修改SkeletalMeshComponent的LOD、更新模式等
// FSequencerSettingScope - 临时修改Sequencer的播放时间、循环模式等
// FConsoleVariableOverrideScope - 临时覆盖控制台变量（如强制LOD）
```

## Demo 示例

以下描述了在编辑器中使用此插件的标准工作流程：

1.  **准备**：打开包含骨骼网格体（Skeletal Mesh）和关卡序列（Level Sequence）的关卡。
2.  **打开序列**：在关卡序列编辑器中打开目标序列，确保骨骼网格体组件正确绑定到序列中的轨道。
3.  **触发烘焙**：在关卡序列编辑器的工具栏中，找到并点击 **“动作（Actions）”** 菜单，然后选择 **“Bake Geometry Cache”**。
4.  **配置**（如适用）：如果插件在烘焙前提供选项（如 `ULevelSequenceGeometryCacheBakerOption` 中的 `NumSamplesPerFrame`），会弹出对话框供用户设置。
5.  **选择保存路径**：在文件浏览器中选择新几何缓存资产的保存路径和名称。
6.  **等待完成**：插件将自动执行：设置场景状态 -> 逐帧播放序列并采集数据 -> 回读数据 -> 写入资产。完成后会恢复场景原始状态。
7.  **结果**：在内容浏览器中找到生成的几何缓存资产，即可在静态网格体组件中使用。

## 模块依赖

从插件模块 `GeometryCacheLevelSequenceBaker` (Runtime) 的用途推断，它很可能依赖以下UE内置模块来实现核心功能：

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 核心依赖，用于创建和写入几何缓存资产 |
| `LevelSequence` | 用于访问和控制关卡序列数据 |
| `SequencerCore` | 提供 `ISequencer` 接口，用于编辑器集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-08-05 | `ae82625a` | Sequencer: Deprecate SetObjectGuid and GetBindings and FMovieSceneBinding constructors. Deprecate Ad | Sequencer API 弃用警告，间接影响该插件调用的接口。 |
| 2025-02-22 | `46650d16` | [GeometryCacheLevelSequenceBaker] Now uses local time instead of global time such that baking from t | 修复了从不同时间点开始烘焙时可能出现的问题，改用局部时间。 |
| 2025-02-21 | `fd076826` | [GeoCacheLevelSeqBaker] Add null checks for material | 增加材质指针空值检查，提升稳定性。 |
| 2025-02-20 | `4b8d0ef7` | [GeometryCacheLevelSequenceBaker] Fixed crash when SKM has MinLOD = some auto generated LOD level. | 修复了当骨骼网格体最小LOD为自动生成层级时导致的崩溃。 |
| 2025-02-20 | `e98d1138` | [GeometryCacheLevelSequenceBaker] Minor fixes: | 初始发布后的次要修复。 |

### 维护评价

该插件是一个**较新的实验性功能**（创建于2025年2月）。在初始提交后，进行了**密集的短期修复和改进**（2月20日至22日），主要解决了稳定性和兼容性问题。最近的更新（2025年8月）是由于其所依赖的Sequencer API发生了弃用变更，表明它仍在被追踪和维护，但功能性更新已暂停。

**综合评价**：
- **状态**：实验性，由 Epic Games 创建。
- **活跃度**：创建初期活跃，近期进入稳定期。
- **风险**：由于其`IsExperimentalVersion=true`，API和行为在UE版本升级时可能会有破坏性变更。依赖已弃用的Sequencer API。
- **推荐**：如果你有明确的“关卡序列动画转几何缓存”需求，可以尝试使用。建议在测试项目中先行验证，并准备好跟进后续版本可能出现的API调整。目前不建议在核心生产管线中依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCacheLevelSequenceBaker)
- [官方文档](https://epicgames.com)（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCacheLevelSequenceBaker)（暂未发现独立测试目录）