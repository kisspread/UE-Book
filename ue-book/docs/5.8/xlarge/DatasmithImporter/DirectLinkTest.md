# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是 Unreal Engine 企业级内容管线的核心组件，负责将工业 CAD、BIM 及其他 3D 建模工具（如 SolidWorks、CATIA、Revit、SketchUp、3ds Max 等）的场景数据导入到 UE 中。它不仅仅是一个简单的文件导入器，而是一整套场景转换与同步框架：

- **Datasmith 文件格式解析**：解析 `.udatasmith` 等原生格式，将其转换为 UE 的 Actor、StaticMesh、Material 等资产
- **DirectLink 实时同步**：通过 DirectLink 协议，实现外部 DCC 工具与 UE 之间的**实时场景同步**，无需反复导出/导入文件
- **翻译器架构**：通过可扩展的 Translator 接口，支持对接不同来源的数据格式（CAD、FBX、glTF 等）
- **外部数据源**：ExternalSource 框架支持从远程或异步来源获取场景数据

本插件默认**未启用**（`EnabledByDefault: false`），需要在项目设置或命令行中手动启用。

## 使用场景

- 你在做**建筑可视化**，需要从 Revit/SketchUp 导入 BIM 模型 → 用 Datasmith 导入 `.udatasmith` 文件
- 你在做**工业数字孪生**，需要从 CATIA/SolidWorks 导入 CAD 装配体 → 用 Datasmith Translator 转换几何体和层级
- 你需要**实时同步**外部 DCC 工具的场景变更到 UE → 用 DirectLink 建立持久连接
- 你在开发**自定义数据导入管线**，需要接入 Datasmith 的翻译器框架 → 实现 `IDatasmithTranslator` 接口

## 蓝图用法

DirectLinkTest 模块提供了一组蓝图可调用的测试节点，用于验证 DirectLink 连接的发送/接收功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TestParameters` | 测试 DirectLink 参数配置是否有效 | `UDirectLinkTestLibrary` |
| `SetupSender` | 初始化 DirectLink 发送端 | `UDirectLinkTestLibrary` |
| `StartSender` | 启动 DirectLink 发送端 | `UDirectLinkTestLibrary` |
| `StopSender` | 停止 DirectLink 发送端 | `UDirectLinkTestLibrary` |
| `SetupReceiver` | 初始化 DirectLink 接收端 | `UDirectLinkTestLibrary` |
| `StartReceiver` | 启动 DirectLink 接收端 | `UDirectLinkTestLibrary` |
| `StopReceiver` | 停止 DirectLink 接收端 | `UDirectLinkTestLibrary` |
| `SendScene` | 通过 DirectLink 发送指定路径的场景文件 | `UDirectLinkTestLibrary` |
| `DumpReceivedScene` | 将已接收的场景数据转储到日志/文件 | `UDirectLinkTestLibrary` |
| `MakeEndpoint` | 创建一个 DirectLink Endpoint（可指定名称和详细日志级别） | `UDirectLinkTestLibrary` |
| `DeleteEndpoint` | 删除指定 Endpoint | `UDirectLinkTestLibrary` |
| `AddPublicSource` | 为 Endpoint 添加公开的 Source 名称 | `UDirectLinkTestLibrary` |
| `AddPublicDestination` | 为 Endpoint 添加公开的 Destination 名称 | `UDirectLinkTestLibrary` |
| `DeleteAllEndpoint` | 删除所有已创建的 Endpoint | `UDirectLinkTestLibrary` |

### 使用示例（蓝图描述）

**测试 DirectLink 发送/接收流程：**

1. 添加 `TestParameters` 节点，确认 DirectLink 参数正确
2. 添加 `SetupSender` → `StartSender` 节点序列，启动发送端
3. 添加 `SetupReceiver` → `StartReceiver` 节点序列，启动接收端
4. 使用 `SendScene` 节点传入一个 `.udatasmith` 文件路径，触发场景发送
5. 使用 `DumpReceivedScene` 节点验证接收端是否正确接收到场景数据
6. 测试结束后调用 `StopSender` 和 `StopReceiver` 清理连接

**手动管理 Endpoint：**

1. 调用 `MakeEndpoint` 创建一个 Endpoint，返回 Endpoint ID（int32）
2. 使用 `AddPublicSource` 或 `AddPublicDestination` 注册 Source/Destination 名称
3. 测试完成后调用 `DeleteEndpoint`（传入 ID）或 `DeleteAllEndpoint` 清理

## C++ 用法

### 头文件引入

```cpp
#include "DirectLinkTestLibrary.h"
#include "DirectLinkTestModule.h"
```

### 基本用法

直接通过蓝图函数库的静态方法调用 DirectLink 测试功能：

```cpp
#include "DirectLinkTestLibrary.h"

// 测试 DirectLink 参数
bool bValid = UDirectLinkTestLibrary::TestParameters();

// 设置并启动发送端
UDirectLinkTestLibrary::SetupSender();
UDirectLinkTestLibrary::StartSender();

// 发送场景
UDirectLinkTestLibrary::SendScene(TEXT("/Game/MyScene.udatasmith"));

// 清理
UDirectLinkTestLibrary::StopSender();
```

### Endpoint 管理用法

```cpp
#include "DirectLinkTestLibrary.h"

// 创建一个 Endpoint
int32 EndpointId = UDirectLinkTestLibrary::MakeEndpoint(TEXT("MyTestEndpoint"), true);

// 注册公开的 Source 和 Destination
UDirectLinkTestLibrary::AddPublicSource(EndpointId, TEXT("MySource"));
UDirectLinkTestLibrary::AddPublicDestination(EndpointId, TEXT("MyDestination"));

// ... 执行测试 ...

// 删除单个 Endpoint
UDirectLinkTestLibrary::DeleteEndpoint(EndpointId);

// 或删除所有 Endpoint
UDirectLinkTestLibrary::DeleteAllEndpoint();
```

### 进阶用法

通过模块访问接口检查 DirectLinkTest 模块的可用性：

```cpp
#include "DirectLinkTestModule.h"

// 检查模块是否已加载
if (FDirectLinkTestModule::IsAvailable())
{
    // 获取模块引用
    FDirectLinkTestModule& Module = FDirectLinkTestModule::Get();
    // 模块已就绪，可以执行 DirectLink 测试
}
```

接收端内部使用 `FTestSceneProvider` 作为 `DirectLink::IConnectionRequestHandler` 实现，管理多个 `FDatasmithSceneReceiver` 实例：

```cpp
#include "TestSceneProvider.h"

// FTestSceneProvider 内部维护了 SceneReceivers 映射
// 每个连接的 Source（按 FGuid 区分）对应一个独立的 FDatasmithSceneReceiver
// CanOpenNewConnection 控制是否接受新连接
// GetSceneReceiver 返回或创建对应的接收器
```

## Demo 示例

### DirectLinkTestActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectLinkTestActor.generated.h"

UCLASS()
class ADirectLinkTestActor : public AActor
{
    GENERATED_BODY()

public:
    ADirectLinkTestActor();

    UFUNCTION(BlueprintCallable, Category = "DirectLink Test")
    void RunFullTest(const FString& SceneFilePath);

    UFUNCTION(BlueprintCallable, Category = "DirectLink Test")
    void Cleanup();

private:
    int32 CurrentEndpointId = -1;
};
```

### DirectLinkTestActor.cpp

```cpp
#include "DirectLinkTestActor.h"
#include "DirectLinkTestLibrary.h"
#include "DirectLinkTestModule.h"

ADirectLinkTestActor::ADirectLinkTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADirectLinkTestActor::RunFullTest(const FString& SceneFilePath)
{
    if (!FDirectLinkTestModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DirectLinkTest module is not available."));
        return;
    }

    // 验证参数
    if (!UDirectLinkTestLibrary::TestParameters())
    {
        UE_LOG(LogTemp, Error, TEXT("DirectLink parameter test failed."));
        return;
    }

    // 创建 Endpoint
    CurrentEndpointId = UDirectLinkTestLibrary::MakeEndpoint(TEXT("TestEndpoint"), true);
    if (CurrentEndpointId < 0)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Endpoint."));
        return;
    }

    // 设置接收端
    UDirectLinkTestLibrary::SetupReceiver();
    UDirectLinkTestLibrary::StartReceiver();

    // 设置发送端
    UDirectLinkTestLibrary::SetupSender();
    UDirectLinkTestLibrary::StartSender();

    // 发送场景
    UDirectLinkTestLibrary::SendScene(SceneFilePath);

    // 转储接收到的场景数据
    UDirectLinkTestLibrary::DumpReceivedScene();

    UE_LOG(LogTemp, Log, TEXT("DirectLink test completed for: %s"), *SceneFilePath);
}

void ADirectLinkTestActor::Cleanup()
{
    UDirectLinkTestLibrary::StopSender();
    UDirectLinkTestLibrary::StopReceiver();

    if (CurrentEndpointId >= 0)
    {
        UDirectLinkTestLibrary::DeleteEndpoint(CurrentEndpointId);
        CurrentEndpointId = -1;
    }
}
```

## 模块依赖

DatasmithImporter 插件包含 8 个模块，以下列出核心依赖关系（省略标准 Core/Engine/Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 核心数据模型（场景描述、资产定义） |
| `DirectLink` | DirectLink 协议底层实现（Endpoint、Source、Destination 管理） |
| `MeshDescription` | 几何体网格数据的中间表示 |
| `MaterialShaderQualitySettings` | 材质和着色器质量配置 |
| `InterchangeCore` | UE5 新一代资产交换框架 |
| `Json` | JSON 序列化（Datasmith 文件格式解析） |
| `RHI` | 渲染硬件接口（纹理和材质处理） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 到新的 UE_LOGF 宏 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced overloads with | 废弃旧版 GetObjects API，引入新重载 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 整理纹理属性修改代码，正确使用 PreEditChange/PostEditChange |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质翻译器功能开发 |

### 维护评价

Datasmith Importer 是 Epic 官方维护的企业级插件，作为 Unreal Engine Enterprise 功能集的一部分持续更新。从近期 commit 来看，该插件仍处于**活跃维护**状态：

- **持续的代码质量改进**：包括浮点精度修复、日志宏迁移、API 废弃替换等基础设施更新
- **功能持续演进**：2026 年 3 月仍有新材质翻译器的开发工作
- **创建于 2019 年**：已有约 7 年历史，经过多代 UE 版本验证，属于成熟的工业级组件

**注意事项**：
- 该插件**默认未启用**，需要在项目设置中手动启用或通过 `-datasmith` 命令行参数加载
- 部分高级功能（如特定 CAD 格式支持）可能需要额外的 Datasmith Content 资产包
- DirectLinkTest 模块主要用于开发和测试阶段，**不建议在生产环境中使用**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [DirectLinkTest 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest)