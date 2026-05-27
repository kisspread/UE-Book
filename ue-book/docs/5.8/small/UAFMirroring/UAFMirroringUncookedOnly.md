# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 镜像 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime), `UAFMirroringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

## 用途

UAF Mirroring 是 **UAF（Unreal Animation Framework）** 系统的一个扩展插件，其核心功能是为 UAF 动画框架提供**关键帧镜像（Keyframe Mirroring）** 的支持。它通过定义镜像特性（Trait）和数据表（MirrorDataTable），使得开发者能够方便地在 UAF 的动画图（AnimGraph）中创建镜像动画，例如将左侧肢体的动画镜像到右侧。这解决了 UAF 框架内部缺乏原生镜像功能的问题，避免了开发者手动编写复杂的镜像逻辑。

## 使用场景

- 你在使用 UAF 构建动画状态机或动画蓝图，并希望基于现有的单侧动画数据（如左手挥砍）快速生成其镜像版本（右手挥砍）。
- 你需要为 UAF 动画图（AnimGraph）创建一个可复用的镜像节点，该节点能够根据预定义的镜像数据表（MirrorDataTable）自动处理骨骼、曲线和属性的映射关系。
- 你正在为 UAF 系统开发自定义的动画特性（Trait），并希望集成镜像功能。

## 蓝图用法

该插件的核心蓝图节点是一个 **UAF 动画图节点模板**，允许在 UAF 的可视化动画图编辑器中直接使用镜像功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mirror` | 使用镜像数据表对输入动画姿态进行镜像处理 | `UUAFGraphNodeTemplate_Mirror` |

### 使用示例（蓝图描述）

1.  在 UAF 动画图编辑器中，右键打开节点菜单，找到 **UAF** 分类下的 **Mirror** 节点并添加到图中。
2.  该节点会自动创建三个输入引脚：`Input`（输入动画姿态）、`Setup`（镜像设置参数）和 `ApplyTo`（应用目标）。
3.  你可以将一个 `MirrorDataTable` 资产直接拖放到该节点上，节点标题会自动更新为 “Mirror using [数据表名称]”，并完成配置。
4.  将需要镜像的动画姿态连接到 `Input` 引脚，设置好 `Setup` 中的参数，节点的输出即为镜像后的动画姿态。

## C++ 用法

### 头文件引入

```cpp
#include "UAFMirroring.h"
// 若需要使用图节点模板
#include "UAFGraphNodeTemplate_Mirror.h"
```

### 基本用法

该插件主要扩展了 UAF 的 Trait 系统。一个基本的镜像功能通常通过 `FMirroringTraitData` 特性来实现。
```cpp
// 在定义 UAF 节点或特性时，使用镜像特性数据
#include "MirroringTraitData.h"

// ... 在某个 UAF 节点或特性定义中
TInstancedStruct<UE::UAF::FMirroringTraitData> MirroringTraitData = TInstancedStruct<UE::UAF::FMirroringTraitData>::Make();
// 配置 MirroringTraitData 中的参数，如指定 MirrorDataTable
```
*（源码参考：`UAFGraphNodeTemplate_Mirror.h` 中 `Traits` 的初始化）*

### 进阶用法

要创建一个完整的自定义镜像图节点模板，需要继承 `UUAFGraphNodeTemplate` 并参考 `UUAFGraphNodeTemplate_Mirror` 的实现。
```cpp
UCLASS()
class UMyCustomMirrorNodeTemplate : public UUAFGraphNodeTemplate
{
    GENERATED_BODY()

    UMyCustomMirrorNodeTemplate()
    {
        Title = LOCTEXT("MyMirrorTitle", "My Mirror");
        // ... 设置其他模板属性
        // 添加镜像特性
        Traits = {
            TInstancedStruct<UE::UAF::FMirroringTraitData>::Make(),
        };
        // 设置拖放资产类型为镜像数据表
        DragDropAssetTypes.Add(UMirrorDataTable::StaticClass());
    }

    // 重写资产拖放和引脚值变更的处理逻辑以更新节点显示
    virtual void HandleAssetDropped_Implementation(UAnimNextController* Controller, URigVMUnitNode* Node, UObject* Asset) const override;
    virtual void HandlePinDefaultValueChanged_Implementation(UAnimNextController* Controller, URigVMPin* Pin) const override;
    virtual void HandleAssetRenamed_Implementation(UAnimNextController* Controller, URigVMNode* Node, const FAssetData& AssetData, const FString& OldName) const override;
};
```

## Demo 示例

以下是一个自定义镜像图节点模板的头文件示例。
```cpp
// MyCustomMirrorNodeTemplate.h
#pragma once

#include "CoreMinimal.h"
#include "UAFGraphNodeTemplate.h"
#include "MirroringTraitData.h"
#include "MyCustomMirrorNodeTemplate.generated.h"

UCLASS()
class UMyCustomMirrorNodeTemplate : public UUAFGraphNodeTemplate
{
	GENERATED_BODY()

	UMyCustomMirrorNodeTemplate()
	{
		Title = LOCTEXT("CustomMirrorTitle", "Custom Mirror");
		TooltipText = LOCTEXT("CustomMirrorTooltip", "A custom mirror node for testing.");
		Category = LOCTEXT("CustomMirrorCategory", "UAF Examples");
		MenuDescription = LOCTEXT("CustomMirrorMenuDesc", "Custom Mirror");
		Color = FLinearColor(FColor(200, 100, 50));

		// 关联镜像特性数据
		Traits =
		{
			TInstancedStruct<UE::UAF::FMirroringTraitData>::Make(),
		};

		// 允许拖放镜像数据表资产
		DragDropAssetTypes.Add(UMirrorDataTable::StaticClass());
	}

	// 可选：重写以自定义节点行为
	// virtual void HandleAssetDropped_Implementation(...) const override;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | 核心 UAF 动画框架 |
| `UAFAnimGraph` | UAF 动画图相关功能 |
| `RigVM` | 节点化动画图系统的底层运行时 |
| `MirrorDataTable` | 提供镜像数据表资产类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`。 |
| 2026-03-10 | `24473b8e` | Fix direct reads of latent SharedData properties in UAF traits | 修复 UAF 特性中直接读取潜在共享数据属性的问题。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为 UAF 插件添加构建和运行低级测试的验证器。 |
| 2026-01-23 | `81bd488d` | UAF fix some incorrect comparison of invalid bone indicies, where 16bit was upcast to 32bit and comp | 修复无效骨骼索引比较的错误，涉及16位到32位的上行转换。 |
| 2026-01-23 | `9735f798` | UAF: Fix rename/move issues | 修复 UAF 中的重命名和移动问题。 |

### 维护评价

-   **状态**：活跃维护中。
-   **创建时间**：该插件于 2025 年 8 月创建，是 UAF 框架的新增实验性模块。
-   **更新频率**：在创建后的约 8 个月内有多次提交，最近一次在 2026 年 4 月，表明项目仍在积极开发。
-   **更新内容**：近期的提交主要集中在修复底层逻辑错误（如骨骼索引比较、属性读取）和提升代码质量（迁移日志宏、添加测试），属于稳定性维护和改进。
-   **已知限制**：作为 `IsExperimentalVersion: true` 的插件，其 API 和功能可能在后续版本中发生变化。
-   **推荐使用**：**适合早期采用者和 UAF 深度用户**。如果你需要为 UAF 添加镜像功能且可以接受实验性 API 的风险，此插件是官方提供的解决方案。普通项目建议等待其进入 Beta 或正式版。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [官方文档]( )
- [测试用例]( )