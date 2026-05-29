# DMX GDTF

> Implementation of the GDTF standard using Unreal Engine types（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DMX 灯光设备描述 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXGDTF` (Runtime), `DMXZip` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-04-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF) | |

## 用途

本插件是 Unreal Engine 虚拟制作（Virtual Production）工具链中，处理灯光设备控制协议标准 **GDTF (General Device Type Format)** 的核心运行时实现。其主要目的是：

1.  **标准化解析**：将符合 GDTF 标准的 XML 设备描述文件（`.gdtf`，通常打包在 `.gdtf` 或 `.zip` 文件中）解析为 Unreal Engine 可用的对象模型。
2.  **类型映射**：将 GDTF 标准中定义的复杂设备类型、属性、几何、行为等数据结构，映射为一组相互关联的 UOject 派生类（如 `UDMXImportGDTF`、`UDMXImportGDTFFixtureType`、`UDMXImportGDTFPhysicalDescriptions` 等），便于蓝图和 C++ 代码访问和操作。
3.  **提供基础服务**：为更上层的 DMX 功能（如 DMX Library、DMX Fixture 抽象、DMX 协议控制）提供可靠的、经过验证的设备描述数据源。它确保了灯光设备在虚拟场景中的行为与真实世界物理设备的规格一致。

## 使用场景

-   你正在制作一个虚拟片场（Virtual Production Stage），需要控制多种品牌和型号的电脑灯（Moving Light）、LED 灯具等。这些灯具的制造商提供了标准的 GDTF 文件。→ 使用本插件在 UE 中加载这些文件，以精确配置每个灯具的 DMX 通道、模式、光束属性等。
-   你正在开发一款影视后期预览（Previz）软件，需要导入灯光设计师在 lighting console 中使用的设备库。→ 通过本插件解析 GDTF 文件，将设备信息无缝集成到你的 UE 项目中。
-   你需要在蓝图或 C++ 中，程序化地创建或修改灯光设备的 DMX 属性，而不希望手动逐个配置。→ 基于本插件解析出的 GDTF 对象模型进行操作。

## 蓝图用法

### 核心节点

核心节点主要集中在 `UDMXGDTFInitialization` 类中，用于从文件或原始数据启动 GDTF 的解析过程。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize From File` | 从磁盘上的 `.gdtf` 文件路径初始化一个 GDTF 描述对象。 | `UDMXGDTFInitialization` |
| `Initialize From Zip File` | 从 `.zip` 压缩包文件路径初始化一个 GDTF 描述对象。 | `UDMXGDTFInitialization` |
| `Initialize From Buffer` | 从内存中的二进制数据（`TArray<uint8>`）初始化一个 GDTF 描述对象。 | `UDMXGDTFInitialization` |
| `Get Fixture Type` | 根据给定的模式（Mode）名称，从初始化的 GDTF 描述中获取特定的灯具类型描述。 | `UDMXImportGDTF` |
| `Get DMX Footprint` | 获取灯具在特定 DMX 模式下占用的 DMX 通道数量（Footprint）。 | `UDMXImportGDTFFixtureType` |

### 使用示例（蓝图描述）

1.  **在蓝图中加载 GDTF 文件并获取设备信息**：
    -   拖拽一个 `Initialize From File` 节点。
    -   将文件路径（例如从 `FileDialog` 节点获取）连接到其 `File Path` 输入。
    -   将该节点的 `Return Value` (GDTF 描述对象) 保存到一个变量中（类型为 `UDMXImportGDTF`）。
    -   从该变量拖出，连接一个 `Get Fixture Type` 节点，输入模式名称（如 “Mode 1”），即可获取到该模式的详细设备描述，进而访问其属性。

## C++ 用法

本插件的 C++ API 主要面向需要深度集成或扩展 GDTF 解析逻辑的开发者。

### 头文件引入

```cpp
// 引入核心 GDTF 类定义
#include "DMXGDTFInitialization.h"
#include "DMXImportGDTF.h"
#include "DMXImportGDTFFixtureType.h"
// ... 其他根据需要引入的特定 GDTF 子模块头文件
```

### 基本用法

以下示例展示如何从文件初始化一个 GDTF 对象并读取基础信息。代码逻辑参考自测试用例 `FDmxGdtfFixtureTypeInitializationTest`。

```cpp
// 来源: Source/DMXGDTFTests/Private/Tests/DMXGdtfFixtureTypeInitializationTest.cpp
#include "DMXGDTFInitialization.h"
#include "DMXImportGDTF.h"
#include "Misc/AutomationTest.h"

// 定义一个简单的测试或函数
void ExampleInitializeGDTF()
{
    // 1. 设置 GDTF 文件的路径
    const FString GDTFFilePath = FPaths::ProjectContentDir() / TEXT("TestFixtures/ValidFixture.gdtf");

    // 2. 使用 UDMXGDTFInitialization 进行初始化
    UDMXGDTFInitialization* Initializer = NewObject<UDMXGDTFInitialization>();
    UDMXImportGDTF* GDTFData = Initializer->InitializeFromFile(GDTFFilePath);

    // 3. 检查初始化是否成功
    if (GDTFData)
    {
        UE_LOG(LogTemp, Log, TEXT("GDTF file initialized successfully. Fixture Type: %s"), *GDTFData->FixtureTypeName);

        // 4. 获取一个具体的灯具类型描述
        const FString ModeName = TEXT("Mode 1");
        UDMXImportGDTFFixtureType* FixtureType = GDTFData->GetFixtureType(ModeName);
        if (FixtureType)
        {
            // 5. 现在可以访问 FixtureType 的属性，例如 DMX Footprint
            int32 DMXFootprint = FixtureType->GetDMXFootprint();
            UE_LOG(LogTemp, Log, TEXT("Mode '%s' DMX Footprint: %d"), *ModeName, DMXFootprint);
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize GDTF file from path: %s"), *GDTFFilePath);
    }
}
```

### 进阶用法

更复杂的场景可能涉及遍历 GDTF 数据结构、处理不同的物理描述、或从内存流中加载。这需要结合 `UDMXImportGDTF`、`UDMXImportGDTFFixtureType`、`UDMXImportGDTFPhysicalDescriptions` 等多个类。

```cpp
// 概念示例，非直接可运行代码，结合了多个 GDTF 子模块
void AdvancedGDTFUsage(UDMXImportGDTF* GDTFData)
{
    if (!GDTFData) return;

    // 遍历所有定义的灯具类型
    for (UDMXImportGDTFFixtureType* FixtureType : GDTFData->FixtureTypes)
    {
        UE_LOG(LogTemp, Log, TEXT("Processing FixtureType: %s"), *FixtureType->Name);

        // 获取该类型下的物理描述信息
        UDMXImportGDTFPhysicalDescriptions* PhysicalDesc = FixtureType->PhysicalDescriptions;
        if (PhysicalDesc)
        {
            // 例如，获取灯泡或 LED 发光源的属性
            // PhysicalDesc->Lamps, PhysicalDesc->Emitters 等
            // ... 进一步操作
        }

        // 遍历该类型下定义的所有 DMX 模式（Mode）
        for (UDMXImportGDTFMode* Mode : FixtureType->Modes)
        {
            // 分析每个模式下的通道布局
            for (UDMXImportGDTFDMXChannel* Channel : Mode->DMXChannels)
            {
                // 处理通道属性，如通道类型、初始值、范围等
                // Channel->ChannelFunction, Channel->Default, Channel->Highlight 等
            }
        }
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在 Actor 中初始化一个 GDTF 文件。

```cpp
// MyGDTFActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGDTFActor.generated.h"

class UDMXImportGDTF;

UCLASS()
class MYPROJECT_API AMyGDTFActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyGDTFActor();

protected:
	virtual void BeginPlay() override;

public:	
	// 要加载的 GDTF 文件名（放在 Content/TestFixtures 目录下）
	UPROPERTY(EditAnywhere, Category = "GDTF Test")
	FString GDTFFileName = TEXT("SampleFixture.gdtf");

private:
	UPROPERTY()
	TObjectPtr<UDMXImportGDTF> LoadedGDTF;
};
```

```cpp
// MyGDTFActor.cpp
#include "MyGDTFActor.h"
#include "DMXGDTFInitialization.h"
#include "DMXImportGDTF.h"
#include "DMXImportGDTFFixtureType.h"
#include "Paths.h"

AMyGDTFActor::AMyGDTFActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyGDTFActor::BeginPlay()
{
	Super::BeginPlay();

	// 构建完整的文件路径
	const FString FullPath = FPaths::ProjectContentDir() / TEXT("TestFixtures") / GDTFFileName;

	// 初始化 GDTF
	UDMXGDTFInitialization* Initializer = NewObject<UDMXGDTFInitialization>();
	LoadedGDTF = Initializer->InitializeFromFile(FullPath);

	if (LoadedGDTF)
	{
		UE_LOG(LogTemp, Log, TEXT("Successfully loaded GDTF: %s"), *GDTFFileName);

		// 尝试获取第一个 Fixture Type
		if (LoadedGDTF->FixtureTypes.Num() > 0)
		{
			UDMXImportGDTFFixtureType* FirstType = LoadedGDTF->FixtureTypes[0];
			UE_LOG(LogTemp, Log, TEXT("First Fixture Type Name: %s"), *FirstType->Name);

			if (FirstType->Modes.Num() > 0)
			{
				UE_LOG(LogTemp, Log, TEXT("First Mode Name: %s, DMX Footprint: %d"),
					*FirstType->Modes[0]->Name,
					FirstType->Modes[0]->GetDMXFootprint());
			}
		}
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to load GDTF file: %s"), *FullPath);
	}
}
```

## 模块依赖

本插件的模块依赖相对独立，主要服务于 DMX 系统内部。

| 模块 | 用途 |
|---|---|
| `DMXZip` | 本插件的依赖项，用于处理 `.gdtf` 文件常见的 ZIP 压缩包格式。 |
| `XMLParser` | 用于解析 GDTF 文件的核心 XML 结构。 |
| `DMXRuntime` | （隐含）作为上层 DMX 功能的提供者，其构建可能依赖本插件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为单精度浮点数时产生的编译器警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了日志打印中 32/64 位格式说明符与参数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件代码中的 UE_LOG 日志宏迁移到新的 UE_LOGF 标准。 |
| 2026-02-02 | `f5e86e73` | DMXGDTF: Fix potential divide by zero | 修复了 DMXGDTF 模块中一个潜在的除以零错误。 |
| 2024-09-26 | `62a80188` | DMX: Move the DMXGDTF header from internal to public | 将 DMXGDTF 模块的主头文件访问权限从内部 (Internal) 改为公开 (Public)，便于其他模块调用。 |

### 维护评价

本插件于 2024 年 4 月创建，目前处于 **活跃维护** 状态。
-   **更新频率**：近期（2026年）有多次提交，虽然主要是编译兼容性、代码规范和细微 bug 修复，但表明其仍被 Epic 内部开发流程所覆盖。
-   **功能性**：最后一次重大功能性更新记录在创建 commit 中（初始开发版本）。后续更新聚焦于稳定性和代码质量。
-   **状态**：作为 Unreal Engine 虚拟制作核心工具链的一部分，其重要性高，不太可能被废弃。
-   **建议**：**推荐使用**。它是处理 GDTF 标准文件的官方且维护中的解决方案。开发者应依赖此插件，而非自行实现 GDTF 解析器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF/Source/DMXGDTFTests/Private/Tests)