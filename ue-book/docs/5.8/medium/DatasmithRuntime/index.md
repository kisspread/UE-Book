# Datasmith Runtime

> Datasmith Runtime

| 属性 | 值 |
|---|---|
| 中文名 | 实时数据同步 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `DatasmithRuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Enterprise/DatasmithRuntime) | |

## 用途

该插件为 Unreal Engine 提供了一种在**运行时（Runtime）** 加载、接收和同步 Datasmith 场景的功能。它主要解决以下问题：
1.  **运行时场景加载**：无需在编辑器中预先导入，可以在游戏或应用程序运行时动态加载来自 CAD、BIM 或其他 3D 软件（如 Revit、CATIA、SketchUp）的场景文件（通过 `ADatasmithRuntimeActor` 和 `UDatasmithRuntimeLibrary::LoadFile`）。
2.  **实时场景同步**：通过集成 DirectLink 协议，该插件能够建立一个直接的“源-目标”连接。这意味着外部设计软件中的场景修改（如模型移动、材质变更）可以**近乎实时地**同步到 Unreal Engine 的运行场景中，实现“设计可视化”或“数字孪生”应用的热更新。
3.  **异步增量处理**：场景的解析、网格构建、材质和纹理创建等繁重任务被拆解为可中断的增量操作，在游戏线程的 Tick 中分帧执行，避免了卡顿，保证了应用程序的流畅性。

## 使用场景

- **建筑/工业设计评审**：您在使用 Revit 或 SolidWorks 进行设计，希望将模型实时传输到 UE 中进行 VR 漫游或高质量渲染。
- **数字孪生**：需要将物理资产的持续变化（来自 BIM 软件或传感器数据处理平台）映射到虚拟世界中。
- **运行时内容分发**：应用程序需要根据用户选择或服务器指令，动态加载不同的 3D 设计方案。
- **跨软件协同**：需要在一个主应用（如 UE）中接收并可视化来自多个不同专业软件的数据流。

## 蓝图用法

蓝图功能主要通过 `UDatasmithRuntimeLibrary` 和 `ADatasmithRuntimeActor` 两个类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadFile` | 使用 Datasmith 翻译器加载指定路径的场景文件到目标 Actor。 | `UDatasmithRuntimeLibrary` |
| `ResetActor` | 重置目标 Actor，清除其已加载的所有场景内容。 | `UDatasmithRuntimeLibrary` |
| `GetDirectLinkProxy` | 获取 DirectLink 端点的代理对象，用于查询网络中的数据源。 | `UDatasmithRuntimeLibrary` |
| `LoadFileFromExplorer` | 弹出系统文件浏览器，让用户选择文件并加载。 | `UDatasmithRuntimeLibrary` |
| `IsConnected` | 检查当前 Runtime Actor 是否已通过 DirectLink 连接到数据源。 | `ADatasmithRuntimeActor` |
| `OpenConnectionWithIndex` | 使用源列表索引建立与指定 DirectLink 数据源的连接。 | `ADatasmithRuntimeActor` |
| `CloseConnection` | 关闭当前的 DirectLink 连接。 | `ADatasmithRuntimeActor` |
| `GetSourceName` | 获取当前连接的 DirectLink 数据源名称。 | `ADatasmithRuntimeActor` |
| `IsReceiving` | 检查是否正在接收场景数据更新。 | `ADatasmithRuntimeActor` |

### 使用示例（蓝图描述）

1.  **加载本地文件**：
    - 在场景中放置一个 `ADatasmithRuntimeActor`。
    - 调用 `UDatasmithRuntimeLibrary::LoadFile`，传入该 Actor 引用和一个文件路径字符串（如 `“C:/Models/Office.rvt”`）。
    - 监听 `ADatasmithRuntimeActor` 的 `Progress` 和 `bBuilding` 属性以跟踪加载进度。

2.  **建立实时连接**：
    - 调用 `UDatasmithRuntimeLibrary::GetDirectLinkProxy` 获取代理对象。
    - 从代理对象的 `GetListOfSources` 节点获取可用数据源列表。
    - 调用 `ADatasmithRuntimeActor::OpenConnectionWithIndex` 并传入想要连接的源索引。
    - 连接成功后，目标 Actor 会自动接收并应用来自该源的所有后续场景变更。

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithRuntime.h"
#include "DatasmithRuntimeBlueprintLibrary.h" // 用于蓝图函数库
```

### 基本用法

**创建并配置 Runtime Actor 并加载文件**（基于 `UDatasmithRuntimeLibrary::LoadFile` 和 `ADatasmithRuntimeActor` 头文件推断）：

```cpp
// 1. 生成 DatasmithRuntime Actor
ADatasmithRuntimeActor* RuntimeActor = GetWorld()->SpawnActor<ADatasmithRuntimeActor>();

// 2. 配置导入选项（可选）
FDatasmithRuntimeImportOptions ImportOptions;
ImportOptions.BuildHierarchy = EBuildHierarchyMethod::Simplified; // 使用简化的层次结构以提高性能
ImportOptions.bImportMetaData = true; // 导入元数据
RuntimeActor->ImportOptions = ImportOptions;

// 3. 加载文件
FString FilePath = TEXT("/Game/MyModels/Chair.obj");
bool bSuccess = UDatasmithRuntimeLibrary::LoadFile(RuntimeActor, FilePath);
```

**使用 DirectLink 监听场景变化**（基于 `UDirectLinkProxy` 和 `ADatasmithRuntimeActor` 头文件推断）：

```cpp
// 1. 获取 DirectLink 代理
UDirectLinkProxy* DirectLinkProxy = UDatasmithRuntimeLibrary::GetDirectLinkProxy();

// 2. 绑定场景变化事件
DirectLinkProxy->OnDirectLinkChange.AddDynamic(this, &AMyClass::OnDirectLinkUpdate);

// 3. 事件处理函数
void AMyClass::OnDirectLinkUpdate()
{
    UE_LOG(LogTemp, Log, TEXT("DirectLink 网络发生变化！"));
    // 可以在此处查询新的源列表或检查连接状态
    TArray<FDatasmithRuntimeSourceInfo> Sources = DirectLinkProxy->GetListOfSources();
}

// 4. 在 Actor 上建立连接
if (RuntimeActor && Sources.Num() > 0)
{
    RuntimeActor->OpenConnectionWithIndex(0); // 连接到列表中的第一个源
}
```

### 进阶用法

**监听资源构建完成事件**（基于 `SceneImporter.h` 中的委托声明）：

```cpp
// 在某个拥有对 FSceneImporter 引用的类中（通常需要自定义逻辑）
DatasmithRuntime::FSceneImporter* Importer = ...; // 获取场景导入器

// 绑定静态网格体完成委托
Importer->OnStaticMeshComplete.AddLambda([](UStaticMesh* NewMesh)
{
    UE_LOG(LogTemp, Log, TEXT("新静态网格体创建完成: %s"), *NewMesh->GetName());
    // 可以在此处为网格体添加额外逻辑
});

// 绑定材质完成委托
Importer->OnMaterialComplete.AddLambda([](UMaterialInstanceDynamic* NewMaterial)
{
    UE_LOG(LogTemp, Log, TEXT("新材质实例创建完成: %s"), *NewMaterial->GetName());
});
```

**手动重置场景**（基于 `ADatasmithRuntimeActor::Reset`）：

```cpp
// 当不再需要当前场景，或需要加载新文件时，先重置 Actor
RuntimeActor->Reset();
// 然后再加载新文件
UDatasmithRuntimeLibrary::LoadFile(RuntimeActor, NewFilePath);
```

## Demo 示例

```cpp
// DatasmithRuntimeDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DatasmithRuntime.h" // 包含 ADatasmithRuntimeActor
#include "DatasmithRuntimeDemo.generated.h"

UCLASS()
class ADatasmithRuntimeDemo : public AActor
{
	GENERATED_BODY()

public:
	ADatasmithRuntimeDemo();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

private:
	UPROPERTY(VisibleAnywhere, Category = "Datasmith")
	TObjectPtr<ADatasmithRuntimeActor> RuntimeActor;

	void OnDirectLinkNetworkChange();
};
```

```cpp
// DatasmithRuntimeDemo.cpp
#include "DatasmithRuntimeDemo.h"
#include "DatasmithRuntimeBlueprintLibrary.h"

ADatasmithRuntimeDemo::ADatasmithRuntimeDemo()
{
	PrimaryActorTick.bCanEverTick = true;
}

void ADatasmithRuntimeDemo::BeginPlay()
{
	Super::BeginPlay();

	// 1. 生成 Datasmith Runtime Actor
	FActorSpawnParameters SpawnParams;
	RuntimeActor = GetWorld()->SpawnActor<ADatasmithRuntimeActor>(FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

	if (RuntimeActor)
	{
		// 2. 绑定 DirectLink 变化事件
		UDirectLinkProxy* Proxy = UDatasmithRuntimeLibrary::GetDirectLinkProxy();
		if (Proxy)
		{
			Proxy->OnDirectLinkChange.AddDynamic(this, &ADatasmithRuntimeDemo::OnDirectLinkNetworkChange);
		}

		// 3. 设置导入选项
		FDatasmithRuntimeImportOptions Options;
		Options.bImportMetaData = true;
		RuntimeActor->ImportOptions = Options;

		// 4. 加载一个示例文件（路径需根据实际情况调整）
		FString SampleFile = FPaths::ProjectContentDir() / TEXT("SampleData/ArchSample.3ds");
		UDatasmithRuntimeLibrary::LoadFile(RuntimeActor, SampleFile);
	}
}

void ADatasmithRuntimeDemo::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 可以在这里检查 RuntimeActor 的状态，例如加载进度
	if (RuntimeActor && RuntimeActor->bBuilding)
	{
		UE_LOG(LogTemp, Log, TEXT("场景构建进度: %.1f%%"), RuntimeActor->Progress * 100.0f);
	}
}

void ADatasmithRuntimeDemo::OnDirectLinkNetworkChange()
{
	UE_LOG(LogTemp, Log, TEXT("DirectLink 网络检测到变化。"));
	// 在此处可以执行查询源列表、重连等逻辑
}
```

## 模块依赖

从 `DatasmithRuntime.Build.cs` 分析，除标准依赖外，需要以下模块：

| 模块 | 用途 |
|---|---|
| `DatasmithRuntime` | 本插件的核心运行时模块。 |
| `DirectLink` | 提供 DirectLink 协议的核心实现，用于场景数据的网络同步。 |
| `DatasmithCore` | 提供 Datasmith 场景的核心数据结构和接口。 |

*注：该插件还依赖 `DatasmithImporter` 和 `UdpMessaging` 插件，已在 `.uplugin` 中声明。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移为 UE_LOGF，属于日志系统现代化更新。 |
| 2025-09-09 | `cee927cb` | Add missing headers. | 添加缺失的头文件包含，属于编译修复。 |
| 2025-07-14 | `8c4cad91` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors... | 修改静态网格体中编辑器专属数据的属性访问方式，涉及底层重构。 |
| 2024-12-11 | `03c93506` | Color functions are [[nodiscard]] | 为颜色函数添加 `[[nodiscard]]` 属性，强调其返回值不应被忽略。 |
| 2024-06-17 | `276d09f6` | Remove all simple usage of REN_ForceNoResetLoaders... | 移除已废弃标志 `REN_ForceNoResetLoaders` 的用法，属于代码清理。 |

### 维护评价

- **创建时间**：插件于 2020 年创建，已有约 5 年历史。
- **最近更新**：最近的几次提交（2024-2026）主要集中在**编译修复、日志系统现代化和底层代码清理**，而非新功能开发。最后一次提及功能的提交需追溯至更早。
- **活跃度**：插件位于 `Experimental` 目录下，且 `.uplugin` 中 `IsBetaVersion=true`、`Installed=false`，表明其仍处于实验性阶段，**未达到稳定发行状态**。更新频率低且内容均为维护性质，表明**开发团队可能已将其搁置或投入极少维护资源**。
- **已知限制**：作为实验性插件，其 API 稳定性、性能优化和错误处理可能不足。平台支持列表（Win64, Mac, Linux）可能未经充分测试。
- **推荐使用**：**谨慎使用**。该插件适合用于**概念验证（PoC）或内部工具开发**，但不建议将其集成到对稳定性和长期支持有要求的商业产品中。若需在运行时导入 Datasmith 场景，建议评估 Epic 官方后续推出的 `DatasmithImporter` 运行时方案或第三方替代品。

**警告：该插件超过 1 年无实质性功能更新，可能已处于维护不活跃状态。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Enterprise/DatasmithRuntime)
- [官方文档]() （无）
- [测试用例]() （未在提供的文件分析中发现标准测试用例）