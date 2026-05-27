# Remote Database Support

> Remote Database Support

| 属性 | 值 |
|---|---|
| 中文名 | 远程数据库支持 |
| 分类 | Database |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteDatabaseSupport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/RemoteDatabaseSupport) | |

## 用途

该插件的核心功能是提供一种通过网络 Socket 连接到远程数据库代理（Database Proxy）的方式。它并非直接连接数据库，而是充当一个客户端，与一个运行在别处（例如专用服务器或开发机）的代理服务进行通信。这种设计允许本身不支持原生数据库功能（如某些主机平台）的游戏引擎实例，能够通过代理来访问和操作数据库。

## 使用场景

- 你的游戏运行在一个没有原生数据库驱动支持的平台（例如旧版主机），但需要记录玩家数据 → 使用此插件连接到一个部署了完整数据库支持的代理服务器。
- 你在开发阶段，希望将游戏的数据库操作集中到一台开发机上进行调试和测试，避免每台开发机都配置本地数据库 → 使用此插件作为客户端连接到中心代理。
- 你需要一个跨平台统一的数据库访问层，将网络通信与数据库操作解耦 → 使用此插件实现客户端，由代理服务处理实际的数据库连接和命令执行。

## 蓝图用法

该插件未暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 节点，因此无法直接在蓝图中使用。其功能完全通过 C++ 接口访问。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteDatabaseConnection.h" // 核心连接类
#include "RemoteDatabaseSupport.h"    // 模块接口
```

### 基本用法

该插件的核心是 `FRemoteDatabaseConnection` 类，它继承自引擎通用的 `FDataBaseConnection` 接口。

```cpp
// 来源于 Source/RemoteDatabaseSupport/Public/RemoteDatabaseConnection.h

// 1. 创建一个远程数据库连接实例
FRemoteDatabaseConnection* RemoteDB = new FRemoteDatabaseConnection();

// 2. 打开连接到远程代理
// ConnectionString: 传递给本地数据库层的字符串（可能留空）
// RemoteConnectionIP: 远程数据库代理的 IP 地址
// RemoteConnectionStringOverride: 代理服务器上使用的实际数据库连接字符串
const TCHAR* ProxyIP = TEXT("192.168.1.100");
const TCHAR* DBConnectionString = TEXT("User=MyUser;Password=MyPass;Database=MyDB;");
bool bSuccess = RemoteDB->Open(TEXT(""), ProxyIP, DBConnectionString);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Successfully connected to remote DB proxy."));
    
    // 3. 执行一条命令
    bool bExecSuccess = RemoteDB->Execute(TEXT("INSERT INTO Players (Name, Score) VALUES ('Player1', 100)"));
    
    // 4. 执行查询并获取结果集
    FDataBaseRecordSet* RecordSet = nullptr;
    bool bQuerySuccess = RemoteDB->Execute(TEXT("SELECT Name, Score FROM Players"), RecordSet);
    
    if (bQuerySuccess && RecordSet)
    {
        // 5. 遍历结果集（FRemoteDataBaseRecordSet 提供了迭代方法）
        // 假设 RecordSet 实际上是 FRemoteDataBaseRecordSet* 类型
        // 在实际使用中，通常由 Execute 函数的内部逻辑返回正确类型的指针。
        while (!RecordSet->IsAtEnd())
        {
            FString PlayerName = RecordSet->GetString(TEXT("Name"));
            int32 PlayerScore = RecordSet->GetInt(TEXT("Score"));
            UE_LOG(LogTemp, Log, TEXT("Player: %s, Score: %d"), *PlayerName, PlayerScore);
            RecordSet->MoveToNext();
        }
        
        // 6. 清理结果集（根据文档注释，调用者负责删除）
        delete RecordSet;
    }
}

// 7. 关闭连接
RemoteDB->Close();

// 8. 清理连接对象
delete RemoteDB;
```

### 进阶用法：使用模块接口

`IRemoteDatabaseSupport` 模块接口主要用于检查模块是否加载，本身不提供数据库操作功能。它通常用于确保插件模块在调用其 API 之前已经就绪。

```cpp
// 来源于 Source/RemoteDatabaseSupport/Public/RemoteDatabaseSupport.h

// 检查模块是否可用
if (IRemoteDatabaseSupport::IsAvailable())
{
    // 获取模块引用（确保模块已加载）
    IRemoteDatabaseSupport& Module = IRemoteDatabaseSupport::Get();
    // 此模块接口主要用于生命周期管理，实际数据库操作使用 FRemoteDatabaseConnection 类
    UE_LOG(LogTemp, Log, TEXT("RemoteDatabaseSupport module is loaded."));
}
```

## Demo 示例

一个最小的、可编译的示例，演示如何连接、执行查询并处理结果。

**DemoDatabaseActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RemoteDatabaseConnection.h"
#include "DemoDatabaseActor.generated.h"

UCLASS()
class ADemoDatabaseActor : public AActor
{
    GENERATED_BODY()

public:
    ADemoDatabaseActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    FRemoteDatabaseConnection* RemoteConnection;
    
    void ConnectAndQuery();
};
```

**DemoDatabaseActor.cpp**
```cpp
#include "DemoDatabaseActor.h"
#include "RemoteDatabaseSupport.h"

ADemoDatabaseActor::ADemoDatabaseActor()
{
    RemoteConnection = nullptr;
}

void ADemoDatabaseActor::BeginPlay()
{
    Super::BeginPlay();
    
    if (IRemoteDatabaseSupport::IsAvailable())
    {
        ConnectAndQuery();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("RemoteDatabaseSupport module is not available!"));
    }
}

void ADemoDatabaseActor::ConnectAndQuery()
{
    RemoteConnection = new FRemoteDatabaseConnection();
    
    // 请替换为实际的远程代理 IP 和数据库连接字符串
    const TCHAR* ProxyIP = TEXT("127.0.0.1");
    const TCHAR* DBConnStr = TEXT("Driver={MySQL ODBC 8.0 Unicode Driver};Server=localhost;Database=testdb;User=root;Password=root;");
    
    if (RemoteConnection->Open(TEXT(""), ProxyIP, DBConnStr))
    {
        UE_LOG(LogTemp, Log, TEXT("Connected to proxy at %s"), ProxyIP);
        
        // 执行一个查询
        FDataBaseRecordSet* Results = nullptr;
        if (RemoteConnection->Execute(TEXT("SELECT 1 + 1 AS Result"), Results))
        {
            // 假设查询返回一行一列
            if (Results && !Results->IsAtEnd())
            {
                int32 ResultValue = Results->GetInt(TEXT("Result"));
                UE_LOG(LogTemp, Log, TEXT("Query Result: %d"), ResultValue);
            }
            // 根据接口文档，调用者负责删除
            delete Results;
            Results = nullptr;
        }
    }
}

void ADemoDatabaseActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (RemoteConnection)
    {
        RemoteConnection->Close();
        delete RemoteConnection;
        RemoteConnection = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

根据插件的 `.uplugin` 文件，它依赖于 `DatabaseSupport` 插件。该插件提供了 `FDataBaseConnection` 和 `FDataBaseRecordSet` 等基类。

| 模块 | 用途 |
|---|---|
| `DatabaseSupport` | 提供数据库连接和记录集的基础抽象接口 (`FDataBaseConnection`, `FDataBaseRecordSet`)。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-04-02 | `f0ec1829` | PR #8660: Fix `bool ExecuteDBProxyCommand()` | 修复 `ExecuteDBProxyCommand` 函数的布尔值返回。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录结构的批量调整或更新。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为安全协议。 |

### 维护评价

该插件创建于 2019 年初，已有约 6 年历史。从 Git 记录看，过去几年几乎没有功能性更新，最近的两次有意义的提交是 2024 年的一个 bug 修复和 2022 年的链接更新。这表明该插件功能已基本稳定，但处于**不活跃维护**状态。它没有被标记为废弃（Deprecated），并且 `EnabledByDefault` 为 `false`，说明它仅用于特定场景。

**结论**：如果你需要在一个不支持原生数据库的平台上通过代理访问数据库，这个插件仍然是一个可选项。但由于长期缺乏功能性更新和文档，使用时可能会遇到边缘情况问题。建议在项目中做好封装，并准备好自行处理可能遇到的兼容性或稳定性问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/RemoteDatabaseSupport)
- 官方文档：无
- 测试用例：未在插件目录内发现标准测试文件。