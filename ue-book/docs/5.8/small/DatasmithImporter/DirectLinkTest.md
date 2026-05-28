# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据矿石导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🆕（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是 Unreal Engine 的企业级数据交换解决方案，用于从多种 CAD、BIM 和 DCC 软件中导入复杂的设计数据。它解决了将专业工程设计软件（如 CATIA、SolidWorks、Revit、SketchUp 等）的模型、材质、灯光和场景数据高效、准确地转换为 UE 可用资产的核心问题。

其存在是为了确保工业可视化、建筑可视化和产品设计等专业领域的数据保真度，保留原始设计意图、层级结构和元数据，避免了通用格式（如 FBX）可能造成的信息丢失和数据退化。

## 使用场景

- 你需要将建筑信息模型（BIM）从 Revit 或 ArchiCAD 导入 Unreal Engine 进行实时渲染和交互式演示。
- 你需要将复杂的 CAD 零件和装配体从 CATIA、NX 或 SolidWorks 导入 UE 进行产品配置器或虚拟装配。
- 你需要从 3ds Max、SketchUp 或 Cinema 4D 导入包含复杂材质和灯光的场景，用于建筑可视化或虚拟制作。
- 你需要保持设计软件中完整的对象层级和命名规范，以便在 UE 中进行程序化操作或数据查询。

## 蓝图用法

Datasmith 插件的核心导入功能通常通过编辑器操作触发，而非直接在蓝图中使用。然而，其部分子模块（如 DirectLink）提供了蓝图可调用的函数用于测试和调试。

### 核心节点

以下节点主要来自 `DirectLinkTest` 模块，用于在运行时测试 DirectLink 连接：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TestParameters` | 测试 DirectLink 连接参数 | `UDirectLinkTestLibrary` |
| `StartReceiver` | 启动 DirectLink 接收器 | `UDirectLinkTestLibrary` |
| `SetupReceiver` | 配置 DirectLink 接收器 | `UDirectLinkTestLibrary` |
| `StopReceiver` | 停止 DirectLink 接收器 | `UDirectLinkTestLibrary` |
| `StartSender` | 启动 DirectLink 发送器 | `UDirectLinkTestLibrary` |
| `SetupSender` | 配置 DirectLink 发送器 | `UDirectLinkTestLibrary` |
| `StopSender` | 停止 DirectLink 发送器 | `UDirectLinkTestLibrary` |
| `SendScene` | 通过 DirectLink 发送场景文件 | `UDirectLinkTestLibrary` |
| `DumpReceivedScene` | 转储已接收的场景数据 | `UDirectLinkTestLibrary` |
| `MakeEndpoint` | 创建一个 DirectLink 端点 | `UDirectLinkTestLibrary` |
| `DeleteEndpoint` | 删除指定的 DirectLink 端点 | `UDirectLinkTestLibrary` |
| `AddPublicSource` | 向端点添加公共源 | `UDirectLinkTestLibrary` |
| `AddPublicDestination` | 向端点添加公共目标 | `UDirectLinkTestLibrary` |
| `DeleteAllEndpoint` | 删除所有 DirectLink 端点 | `UDirectLinkTestLibrary` |

### 使用示例（蓝图描述）

要测试 DirectLink 的基本发送/接收功能，可以在蓝图中按以下步骤操作：
1.  调用 `SetupSender` 节点初始化发送端。
2.  调用 `SetupReceiver` 节点初始化接收端。
3.  调用 `SendScene` 节点，输入要发送的 `.udatasmith` 文件路径。
4.  调用 `DumpReceivedScene` 节点，检查接收端是否成功接收到场景数据。
5.  最后，调用 `StopSender` 和 `StopReceiver` 清理资源。

## C++ 用法

Datasmith 的核心功能通常通过 C++ 接口在编辑器扩展或自定义导入器中使用。以下示例基于其提供的 `UDirectLinkTestLibrary` 类。

### 头文件引入

```cpp
#include "DirectLinkTest/Public/DirectLinkTestLibrary.h"
```

### 基本用法

通过 `UDirectLinkTestLibrary` 提供的静态函数，可以在 C++ 中调用 DirectLink 的测试功能。

```cpp
// 来源：引擎提供的测试库头文件 DirectLinkTestLibrary.h
// 测试 DirectLink 的基本收发流程
void TestDirectLinkConnection()
{
    // 配置并启动接收器
    if (UDirectLinkTestLibrary::SetupReceiver() && UDirectLinkTestLibrary::StartReceiver())
    {
        // 配置并启动发送器
        if (UDirectLinkTestLibrary::SetupSender() && UDirectLinkTestLibrary::StartSender())
        {
            // 发送一个场景文件
            FString DatasmithFilePath = TEXT("Path/To/YourScene.udatasmith");
            bool bSendSuccess = UDirectLinkTestLibrary::SendScene(DatasmithFilePath);
            if (bSendSuccess)
            {
                // 检查接收端是否收到数据
                UDirectLinkTestLibrary::DumpReceivedScene();
            }
            // 停止发送和接收
            UDirectLinkTestLibrary::StopSender();
        }
        UDirectLinkTestLibrary::StopReceiver();
    }
}
```

### 进阶用法

使用 `MakeEndpoint` 和 `AddPublicSource`/`AddPublicDestination` 接口创建自定义的 DirectLink 端点和连接。

```cpp
// 来源：引擎提供的测试库头文件 DirectLinkTestLibrary.h
// 创建一个具有公共源和目标的端点
void CreateCustomDirectLinkEndpoint()
{
    // 创建一个名为 “MyEndpoint” 的端点
    int32 EndpointId = UDirectLinkTestLibrary::MakeEndpoint(TEXT("MyEndpoint"), true);
    if (EndpointId != INDEX_NONE)
    {
        // 为该端点添加一个公共源
        UDirectLinkTestLibrary::AddPublicSource(EndpointId, TEXT("MySource"));
        // 为该端点添加一个公共目标
        UDirectLinkTestLibrary::AddPublicDestination(EndpointId, TEXT("MyDestination"));
        
        // ... 执行使用该端点进行数据交换的逻辑 ...
        
        // 清理：删除端点
        UDirectLinkTestLibrary::DeleteEndpoint(EndpointId);
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 类，用于集成 DirectLink 测试功能。

**MyDirectLinkTestActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDirectLinkTestActor.generated.h"

UCLASS()
class MYPROJECT_API AMyDirectLinkTestActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyDirectLinkTestActor();

protected:
	virtual void BeginPlay() override;

public:	
	UFUNCTION(BlueprintCallable, Category = "DirectLinkTest")
	void RunFullDirectLinkTest(const FString& SceneFilePath);

	UFUNCTION(BlueprintCallable, Category = "DirectLinkTest")
	void SetupAndRunEndpointTest();

private:
	bool bIsSetupComplete = false;
};
```

**MyDirectLinkTestActor.cpp**
```cpp
#include "MyDirectLinkTestActor.h"
#include "DirectLinkTestLibrary.h" // 包含测试库头文件

AMyDirectLinkTestActor::AMyDirectLinkTestActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyDirectLinkTestActor::BeginPlay()
{
	Super::BeginPlay();
	// 可在此处进行初始化，例如检查 DirectLink 模块是否可用
}

void AMyDirectLinkTestActor::RunFullDirectLinkTest(const FString& SceneFilePath)
{
	if (!bIsSetupComplete)
	{
		if (UDirectLinkTestLibrary::SetupReceiver() && UDirectLinkTestLibrary::SetupSender())
		{
			bIsSetupComplete = true;
			UE_LOG(LogTemp, Log, TEXT("DirectLink 发送器和接收器设置完成。"));
		}
		else
		{
			UE_LOG(LogTemp, Error, TEXT("DirectLink 设置失败。"));
			return;
		}
	}

	if (UDirectLinkTestLibrary::StartReceiver() && UDirectLinkTestLibrary::StartSender())
	{
		if (UDirectLinkTestLibrary::SendScene(SceneFilePath))
		{
			UE_LOG(LogTemp, Log, TEXT("场景发送成功。正在转储接收到的数据..."));
			UDirectLinkTestLibrary::DumpReceivedScene();
		}
		else
		{
			UE_LOG(LogTemp, Error, TEXT("场景发送失败。"));
		}
		UDirectLinkTestLibrary::StopSender();
		UDirectLinkTestLibrary::StopReceiver();
	}
}

void AMyDirectLinkTestActor::SetupAndRunEndpointTest()
{
	// 创建端点
	int32 EndpointId = UDirectLinkTestLibrary::MakeEndpoint(TEXT("TestActorEndpoint"), true);
	if (EndpointId == INDEX_NONE)
	{
		UE_LOG(LogTemp, Error, TEXT("无法创建 DirectLink 端点。"));
		return;
	}

	// 添加公共源和目标
	UDirectLinkTestLibrary::AddPublicSource(EndpointId, TEXT("TestSource"));
	UDirectLinkTestLibrary::AddPublicDestination(EndpointId, TEXT("TestDestination"));

	UE_LOG(LogTemp, Log, TEXT("DirectLink 端点 (ID: %d) 创建成功，并添加了源和目标。"), EndpointId);

	// 此处可以添加使用该端点进行数据交换的代码

	// 清理：删除端点
	if (UDirectLinkTestLibrary::DeleteEndpoint(EndpointId))
	{
		UE_LOG(LogTemp, Log, TEXT("DirectLink 端点 (ID: %d) 已删除。"), EndpointId);
	}
}
```

## 模块依赖

要使用 Datasmith Importer 插件，你的模块通常需要依赖其核心的 `DatasmithImporter` 模块。对于使用 `DirectLinkTest` 的特定功能，需要依赖以下模块。

| 模块 | 用途 |
|---|---|
| `DatasmithImporter` | Datasmith 导入器的核心功能 |
| `DatasmithTranslator` | Datasmith 文件格式的翻译层 |
| `DirectLinkExtension` | DirectLink 实时连接的运行时扩展 |
| `DirectLinkExtensionEditor` | DirectLink 连接的编辑器扩展 |
| `DirectLinkTest` | DirectLink 连接的测试和调试工具库 |
| `ExternalSource` | 外部数据源管理 |

*注意：由于此插件默认未启用 (`EnabledByDefault: false`)，你需要在项目的 `.uproject` 文件或插件设置中手动启用 `DatasmithImporter`。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数时产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 日志宏迁移到新的 UE_LOGF 宏。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了接受 bIncludeNestedObjects 参数的 GetObjects*/ForEachObjectWithOuter 函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理代码，确保在修改纹理属性时按要求包装在 PreEditChange/PostEditChange 中。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质翻译器工作：（具体功能待后续提交完善）。 |

### 维护评价

Datasmith Importer 作为 Epic Games 企业战略的重要组成部分，处于**持续活跃维护**状态。
-   **年龄**：创建于 2019 年，是一个相对成熟但仍在不断演进的产品。
-   **维护频率**：从 git 历史看，在 2026 年上半年仍有规律的代码更新和改进，表明项目团队在持续投入。
-   **更新内容**：近期更新主要集中在代码质量（修复警告、代码清理）、API 规范化（宏迁移、函数废弃）和新功能开发（材质翻译器）上，属于健康的维护活动。
-   **已知限制**：该插件功能强大，但配置和使用可能较为复杂，需要参考详细的官方文档。DirectLink 功能主要用于高级场景和测试，普通导入工作流通常通过编辑器的 Datasmith 导入器 UI 完成。
-   **推荐使用**：**强烈推荐**用于需要从专业设计软件导入高质量资产的项目。它已成为 UE 在建筑、工程和施工（AEC）以及产品设计领域的标准工作流工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest) (当前仅 DirectLinkTest 模块可见，其他模块测试用例需进一步探索)