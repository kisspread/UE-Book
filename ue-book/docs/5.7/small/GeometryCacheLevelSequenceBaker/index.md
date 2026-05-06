# GeometryCacheLevelSequenceBaker

> Bake Skeletal Meshes in Level Sequence to Geometry Cache

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存序列烘焙器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCacheLevelSequenceBaker` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCacheLevelSequenceBaker) | |

## 用途

该插件是一个编辑器工具，允许用户在 **Level Sequence** 中直接将 **Skeletal Mesh Actor**（或骨骼网格体组件）的动画烘焙为 **Geometry Cache** 资产。它通过 Sequencer 的右键菜单或专用命令，自动解析绑定中的骨骼网格体，逐帧采样位置/变形/蒙皮信息，并输出为常拓扑的几何缓存文件，从而大幅提升运行时渲染性能并简化资产依赖。

原本需要手动导出并调整的流程现在被一键化，且支持烘焙选项（如每帧采样数）和多绑定同时烘焙。

## 使用场景

- 在 Sequencer 中制作过场动画时，希望将角色（Skeletal Mesh）转换为 Geometry Cache，以获得更好的实时性能。
- 需要将一段动画序列导出为独立几何缓存，用于跨关卡、跨项目复用，或作为优化 LOD 策略的一部分。
- 需要对多个 Skeletal Mesh 组件同时烘焙，避免逐个手动处理的繁琐工作。

## 蓝图用法

本插件为纯编辑器工具，**不提供任何可在蓝图或运行时调用的函数**。所有功能通过 Sequencer 界面和 C++ API 暴露。

### 菜单操作

1. 打开 Level Sequence 并选择包含 Skeletal Mesh 的绑定轨道。
2. 在绑定上右键 → **Bake Skeletal Mesh to Geometry Cache**（由插件注册的命令）。
3. 在弹出的文件对话框中选择输出路径和资产名称。
4. 等待进度条完成，生成的 Geometry Cache 资产将出现在内容浏览器。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheLevelSequenceBaker.h"
```

### 基本用法

通过静态方法 `FGeometryCacheLevelSequenceBaker::Bake` 触发烘焙，需要传入一个有效的 `ISequencer` 引用。

```cpp
// 假设你已经持有 Sequencer 实例 TSharedRef<ISequencer> MySequencer
FGeometryCacheLevelSequenceBaker::Bake(MySequencer);
```

该函数内部会：
1. 调用 `GetBindingsToBake` 筛选所有绑定了 Skeletal Mesh 的轨道。
2. 为每个绑定创建 `FComponentInfo`，记录骨骼网格体资产、材质、变换等信息。
3. 逐帧采样顶点位置、法线、切线和 UV，使用 `FGeometryCacheConstantTopologyWriter` 写入资源。
4. 最终生成 `UGeometryCache` 资产并保存到用户指定的路径。

### 进阶用法

你也可以手动控制烘焙流程，例如只获取待烘焙的绑定列表：

```cpp
TArray<FGuid> Bindings = FGeometryCacheLevelSequenceBaker::GetBindingsToBake(MySequencer);
```

或者调用文件路径选择对话框：

```cpp
FString OutPackageName, OutAssetName;
bool bOK = FGeometryCacheLevelSequenceBaker::GetGeometryCacheAssetPathFromUser(OutPackageName, OutAssetName);
```

**来源**：`Engine/Plugins/Experimental/GeometryCacheLevelSequenceBaker/Source/GeometryCacheLevelSequenceBaker/Private/GeometryCacheLevelSequenceBaker.h`

### 扩展 Sequencer 菜单

若要手动注册自定义命令（插件已自动注册），可以参考：

```cpp
// 在模块 StartupModule 中
FGeometryCacheLevelSequenceBakerCommands::Register();
```

## Demo 示例

以下是一个完整的 C++ 模块示例，演示如何在自定义编辑器工具中调用烘焙功能。

### .h

```cpp
// MyBakerTool.h
#pragma once
#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class ISequencer;

class SMyBakerTool : public SCompoundWidget
{
public:
	SLATE_BEGIN_ARGS(SMyBakerTool) {}
	SLATE_END_ARGS()

	void Construct(const FArguments& InArgs);
	void BakeCurrentSequence();
	TSharedPtr<ISequencer> GetActiveSequencer() const;
};
```

### .cpp

```cpp
// MyBakerTool.cpp
#include "MyBakerTool.h"
#include "GeometryCacheLevelSequenceBaker.h"
#include "ISequencer.h"
#include "Sequencer/Public/ISequencerModule.h"

void SMyBakerTool::Construct(const FArguments& InArgs)
{
	ChildSlot
	[
		SNew(SButton)
		.Text(INVTEXT("Bake Selected Skeletal Meshes"))
		.OnClicked(this, &SMyBakerTool::BakeCurrentSequence)
	];
}

void SMyBakerTool::BakeCurrentSequence()
{
	TSharedPtr<ISequencer> Sequencer = GetActiveSequencer();
	if (Sequencer.IsValid())
	{
		FGeometryCacheLevelSequenceBaker::Bake(Sequencer.ToSharedRef());
	}
}

TSharedPtr<ISequencer> SMyBakerTool::GetActiveSequencer() const
{
	// 实际项目中可通过 SequencerModule 或全局引用获取
	return nullptr; // 占位
}
```

## 模块依赖

**需查看插件的 Build.cs 确认完整依赖**。以下为从代码中推断出的必要依赖：

| 模块 | 用途 |
|---|---|
| `Sequencer` | 核心 Sequencer 接口、自定义命令、菜单扩展 |
| `LevelSequence` | Level Sequence 资产类型 |
| `GeometryCache` | Geometry Cache 资产创建与写入 |
| `GeometryCacheStreamer` | 几何缓存流式写入支持 |
| `MovieScene` | 电影场景绑定、轨道数据结构 |
| `UnrealEd` | 编辑器 UI、文件对话框、进度条 |

**注意**：虽然模块类型标记为 `Runtime`，但实际功能仅用于编辑器。使用时需确保项目启用了 `Sequencer` 和 `GeometryCache` 插件。

## 维护状态

### 近期更新

- 2025-08-05 `ae82625a` — Sequencer: Deprecate SetObjectGuid and GetBindings and FMovieSceneBinding constructors.（全局重构，间接影响）
- 2025-02-22 `46650d16` — [GeometryCacheLevelSequenceBaker] Now uses local time instead of global time such that baking from...
- 2025-02-21 `fd076826` — [GeoCacheLevelSeqBaker] Add null checks for material
- 2025-02-20 `4b8d0ef7` — [GeometryCacheLevelSequenceBaker] Fixed crash when SKM has MinLOD = some auto generated LOD level.
- 2025-02-20 `e98d1138` — [GeometryCacheLevelSequenceBaker] Minor fixes

### 维护评价

- **创建时间**：2025-02-20
- **近期更新**：最后一次功能性提交在 2025-02-22，随后只有一次全局代码整理间接影响（2025-08-05）。插件属于刚发布的新工具，基础功能已稳定。
- **活跃度**：自创建后约 5 个月内进行了多次修复，已基本完善，目前处于 **维护中** 阶段（无新功能增加）。
- **风险**：标记为实验性（`IsExperimentalVersion=true`），API 和内部行为可能在未来版本变更。
- **推荐**：适合需要快速烘焙骨骼网格体为几何缓存的编辑工作，建议手动启用并注意版本兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCacheLevelSequenceBaker)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCacheLevelSequenceBaker/Source/GeometryCacheLevelSequenceBaker/Private)（位于同一目录）