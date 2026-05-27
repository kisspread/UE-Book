# Remote Database Support

> Remote Database Support

| 属性 | 值 |
|---|---|
| 中文名 | 远程数据库代理 |
| 分类 | Database |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteDatabaseSupport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/RemoteDatabaseSupport) | |

## 用途

这个插件提供了一个**远程数据库代理客户端**，用于通过网络 Socket 连接到一个数据库代理服务器。它解决的核心问题是：**为没有原生数据库支持的平台提供数据库访问能力**。

许多移动平台或嵌入式平台可能没有本地的 SQLite 或其他数据库库。通过这个插件，UE 应用程序可以连接到一台运行了数据库代理服务的服务器，将 SQL 命令通过 Socket 发送给代理执行，再接收结果，从而实现跨平台的数据库访问。

## 使用场景

- 你的游戏需要在**移动设备**（如 iOS/Android）上存储玩家数据，但该平台无法直接使用本地数据库库。
- 你正在开发一个**跨平台应用**，需要统一的数据库访问接口，而不关心底层平台是否原生支持数据库。
- 你希望将数据库处理逻辑集中到一台**服务器或代理**上，客户端只负责发送命令和接收数据。

## 蓝图用法

在公共头文件 (`Public/*.h`) 中没有发现标记为 `BlueprintCallable` 或 `BlueprintReadWrite` 的蓝图可访问函数或属性。这个插件主要面向 C++ 开发者，通过代码进行调用。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteDatabaseConnection.h"
```

### 基本用法

核心类是 `FRemoteDatabaseConnection`，它继承自数据库基类 `FDataBaseConnection`。

```cpp
// 创建一个远程数据库连接实例
FRemoteDatabaseConnection* Connection = new FRemoteDatabaseConnection();

// 定义连接参数
const TCHAR* ConnectionString = TEXT("MyDBConnectionString");
const TCHAR* RemoteIP = TEXT("192.168.1.100"); // 数据库代理服务器的IP
const TCHAR* RemoteOverrideString = TEXT("RemoteDBName"); // 可选的覆盖连接字符串

// 打开连接
bool bSuccess = Connection->Open(ConnectionString, RemoteIP, RemoteOverrideString);
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Successfully connected to remote database proxy."));
    
    // 执行一个不返回结果的SQL命令（例如 INSERT, UPDATE）
    const TCHAR* InsertCommand = TEXT("INSERT INTO Players (Name, Score) VALUES ('Hero', 100)");
    bool bExecuted = Connection->Execute(InsertCommand);
    
    if (bExecuted)
    {
        UE_LOG(LogTemp, Log, TEXT("Command executed successfully."));
    }
    
    // 关闭连接
    Connection->Close();
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Failed to connect to remote database proxy."));
}

// 清理
delete Connection;
```

### 进阶用法

`Execute` 方法有一个重载版本可以接收一个 `FDataBaseRecordSet` 指针，用于处理 SELECT 查询返回的结果集。

```cpp
FRemoteDatabaseConnection* Connection = new FRemoteDatabaseConnection();
Connection->Open(ConnectionString, RemoteIP, RemoteOverrideString);

const TCHAR* SelectCommand = TEXT("SELECT * FROM Players WHERE Score > 50");
FDataBaseRecordSet* RecordSet = nullptr;

// 执行查询并获取结果集
bool bSuccess = Connection->Execute(SelectCommand, RecordSet);
if (bSuccess && RecordSet)
{
    // 遍历结果集
    for (RecordSet->MoveToFirst(); !RecordSet->IsAtEnd(); RecordSet->MoveToNext())
    {
        FString PlayerName = RecordSet->GetString(TEXT("Name"));
        int32 PlayerScore = RecordSet->GetInt(TEXT("Score"));
        UE_LOG(LogTemp, Log, TEXT("Player: %s, Score: %d"), *PlayerName, PlayerScore);
    }
    
    // 调用者负责删除 RecordSet
    delete RecordSet;
}

Connection->Close();
delete Connection;
```

## Demo 示例

一个完整的、最小化的远程数据库连接和查询示例。

### .h 文件

```cpp
// RemoteDBDemo.h
#pragma once

class FRemoteDatabaseConnection;

class FRemoteDBDemo
{
public:
    void RunDemo();
    
private:
    FRemoteDatabaseConnection* DatabaseConnection = nullptr;
    
    bool ConnectToProxy(const FString& IP);
    void InsertPlayerData(const FString& PlayerName, int32 Score);
    void QueryPlayerData();
    void Disconnect();
};
```

### .cpp 文件

```cpp
// RemoteDBDemo.cpp
#include "RemoteDBDemo.h"
#include "RemoteDatabaseConnection.h" // 确保 Build.cs 中依赖了 RemoteDatabaseSupport 模块

void FRemoteDBDemo::RunDemo()
{
    // 1. 连接到代理服务器
    if (!ConnectToProxy(TEXT("127.0.0.1")))
    {
        UE_LOG(LogTemp, Error, TEXT("Demo: Connection failed."));
        return;
    }
    
    // 2. 插入数据
    InsertPlayerData(TEXT("UnrealPlayer"), 9500);
    
    // 3. 查询数据
    QueryPlayerData();
    
    // 4. 断开连接
    Disconnect();
}

bool FRemoteDBDemo::ConnectToProxy(const FString& IP)
{
    DatabaseConnection = new FRemoteDatabaseConnection();
    // 使用一个简单的连接字符串。实际使用时，RemoteConnectionStringOverride 可能包含数据库名等信息。
    return DatabaseConnection->Open(TEXT(""), *IP, TEXT("GameDatabase"));
}

void FRemoteDBDemo::InsertPlayerData(const FString& PlayerName, int32 Score)
{
    if (!DatabaseConnection) return;
    
    FString Command = FString::Printf(TEXT("INSERT INTO Players (Name, Score) VALUES ('%s', %d)"), *PlayerName, Score);
    bool bSuccess = DatabaseConnection->Execute(*Command);
    UE_LOG(LogTemp, Log, TEXT("Insert %s: %s"), *PlayerName, bSuccess ? TEXT("Success") : TEXT("Failed"));
}

void FRemoteDBDemo::QueryPlayerData()
{
    if (!DatabaseConnection) return;
    
    FDataBaseRecordSet* RecordSet = nullptr;
    bool bSuccess = DatabaseConnection->Execute(TEXT("SELECT Name, Score FROM Players"), RecordSet);
    
    if (bSuccess && RecordSet)
    {
        UE_LOG(LogTemp, Log, TEXT("--- Player List ---"));
        for (RecordSet->MoveToFirst(); !RecordSet->IsAtEnd(); RecordSet->MoveToNext())
        {
            FString Name = RecordSet->GetString(TEXT("Name"));
            int32 Score = RecordSet->GetInt(TEXT("Score"));
            UE_LOG(LogTemp, Log, TEXT("Player: %s, Score: %d"), *Name, Score);
        }
        delete RecordSet;
    }
}

void FRemoteDBDemo::Disconnect()
{
    if (DatabaseConnection)
    {
        DatabaseConnection->Close();
        delete DatabaseConnection;
        DatabaseConnection = nullptr;
        UE_LOG(LogTemp, Log, TEXT("Disconnected from database proxy."));
    }
}
```

## 模块依赖

要使用此插件，你的模块需要在 `Build.cs` 文件中添加对 `RemoteDatabaseSupport` 模块的依赖。

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "RemoteDatabaseSupport" // 添加这一行
});
```

此外，该插件还依赖于 `DatabaseSupport` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-04-02 | `f0ec1829` | PR #8660: Fix `bool ExecuteDBProxyCommand()` | 修复了数据库代理命令执行函数的返回值逻辑错误。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 通用的引擎插件仓库结构整理或迁移。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的第三方链接更新为使用安全协议（如HTTPS）。 |
| 2019-12-27 | `360d078c` | Second batch of remaining Engine copyright updates. | 第二批次的引擎版权信息更新。 |
| 2019-02-04 | `d3f54b21` | Fix CreateSocket and CreateInternetAddr functional usage so they no longer use the deprecated method | 修复了创建 Socket 和网络地址的方法，停止使用已废弃的API。 |

### 维护评价

该插件创建于 2019 年初，是一个较为成熟的“老”插件。最近的实质性更新是 **2024 年 4 月** 对核心函数 `ExecuteDBProxyCommand` 的 bug 修复，表明它**仍在被维护和关注**，但并非活跃的功能开发。

其功能范围明确且稳定，主要用于通过 Socket 连接远程数据库代理。它**不推荐**用于需要复杂本地数据库操作或追求最新特性的场景，但对于其设计初衷——**跨平台远程数据库访问**——它是一个稳定可靠的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/RemoteDatabaseSupport)
- [官方文档]()（无）
- [测试用例]()（未在插件目录内发现标准测试文件）