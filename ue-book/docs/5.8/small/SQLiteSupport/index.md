# SQLite Support

> SQLite Database Support

| 属性 | 值 |
|---|---|
| 中文名 | SQLite 数据库支持 |
| 分类 | Database |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SQLiteSupport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/SQLiteSupport) | |

## 用途

此插件为虚幻引擎项目提供了对 SQLite 数据库的运行时支持。它封装了 SQLite 的核心 API，使开发者能够在 UE 项目中方便地打开、连接、执行 SQL 命令以及处理查询结果集。该插件主要用于需要在客户端或独立服务器上使用轻量级、无需服务器进程的嵌入式数据库的场景，例如本地数据存储、缓存或离线数据处理。

## 使用场景

- 你需要为游戏或应用创建一个本地数据库，用于保存玩家设置、游戏进度或动态生成的关卡数据。
- 你的工具或编辑器扩展需要离线存储或处理结构化数据。
- 项目需要集成一个轻量级的数据库解决方案，无需部署和管理外部数据库服务器（如 MySQL、PostgreSQL）。

## 蓝图用法

该插件主要提供 C++ 接口，蓝图中直接操作数据库连接和结果集的功能相对有限，但可通过核心类暴露的函数进行基础操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open` | 打开指定的 SQLite 数据库文件。 | `FSQLiteDatabaseConnection` |
| `Execute` | 执行一个 SQL 命令（如 INSERT, UPDATE, CREATE TABLE）。 | `FSQLiteDatabaseConnection` |
| `Execute (with ResultSet)` | 执行查询（如 SELECT）并获取结果集。调用者负责管理 `FSQLiteResultSet` 的生命周期。 | `FSQLiteDatabaseConnection` |
| `Close` | 关闭数据库连接并释放文件锁。 | `FSQLiteDatabaseConnection` |
| `GetString` | 从结果集的当前行中，按列名获取一个字符串值。 | `FSQLiteResultSet` |
| `GetInt` | 从结果集的当前行中，按列名获取一个整数值。 | `FSQLiteResultSet` |
| `GetFloat` | 从结果集的当前行中，按列名获取一个浮点数值。 | `FSQLiteResultSet` |
| `GetBigInt` | 从结果集的当前行中，按列名获取一个 64 位整数值。 | `FSQLiteResultSet` |
| `MoveToFirst` | 将结果集游标移动到第一行。 | `FSQLiteResultSet` |
| `MoveToNext` | 将结果集游标移动到下一行。 | `FSQLiteResultSet` |
| `IsAtEnd` | 检查结果集游标是否已到达末尾。 | `FSQLiteResultSet` |

### 使用示例（蓝图描述）

由于蓝图节点截图限制，请按以下逻辑连接：
1.  创建一个 `FSQLiteDatabaseConnection` 对象。
2.  调用 `Open` 节点，连接字符串设为你的数据库文件路径（如 `“Game/SaveData.db”`）。
3.  对于写操作，调用 `Execute` 节点，传入 SQL 语句字符串（如 `“INSERT INTO Players (Name) VALUES (‘Alice’)”`）。
4.  对于读操作，调用 `Execute (with ResultSet)` 节点，传入查询语句（如 `“SELECT * FROM Players”`），并保存输出的 `FSQLiteResultSet`。
5.  使用 `MoveToFirst` 和 `IsAtEnd` 配合循环，遍历结果集中的每一行。
6.  在循环内，使用 `GetString`、`GetInt` 等节点按列名获取数据。
7.  操作完成后，调用 `Close` 关闭连接。

## C++ 用法

### 头文件引入

```cpp
#include "SQLiteDatabaseConnection.h"
#include "SQLiteResultSet.h"
```

### 基本用法

一个简单的数据库操作流程，包含创建表、插入数据和查询数据。
**（注：以下为基于公开 API 推导的典型用法，非来自特定测试用例文件）**

```cpp
// 假设在某个 UObject 或 Actor 中使用
#include "SQLiteDatabaseConnection.h"
#include "SQLiteResultSet.h"

// 创建一个数据库连接对象
FSQLiteDatabaseConnection DatabaseConnection;

// 打开或创建数据库文件
bool bSuccess = DatabaseConnection.Open(TEXT("Game/MySaveData.db"), nullptr, nullptr);
if (bSuccess)
{
    // 创建一个表
    DatabaseConnection.Execute(TEXT("CREATE TABLE IF NOT EXISTS Players (ID INTEGER PRIMARY KEY, Name TEXT)"));
    
    // 插入数据
    DatabaseConnection.Execute(TEXT("INSERT INTO Players (ID, Name) VALUES (1, 'PlayerOne')"));
    
    // 查询数据
    FSQLiteResultSet* ResultSet = nullptr;
    DatabaseConnection.Execute(TEXT("SELECT * FROM Players"), ResultSet);
    
    if (ResultSet && !ResultSet->HasError())
    {
        // 移动到第一行
        ResultSet->MoveToFirst();
        
        // 遍历所有行
        while (!ResultSet->IsAtEnd())
        {
            FString PlayerName = ResultSet->GetString(TEXT("Name"));
            int32 PlayerID = ResultSet->GetInt(TEXT("ID"));
            
            UE_LOG(LogTemp, Log, TEXT("Player Found: ID=%d, Name=%s"), PlayerID, *PlayerName);
            
            ResultSet->MoveToNext();
        }
        
        // 清理结果集
        delete ResultSet;
    }
    
    // 关闭连接
    DatabaseConnection.Close();
}
```

### 进阶用法

结合 `SQLiteCore` 模块（该插件的依赖项）使用预处理语句，可以更安全、高效地执行参数化查询。
**（需要额外包含 SQLiteCore 的头文件，如 `#include “SQLitePreparedStatement.h”`）**

## Demo 示例

一个最小化的数据库操作示例，展示从创建到查询的完整流程。

```cpp
// 文件: MyDBManager.h
#pragma once

#include "CoreMinimal.h"
#include "SQLiteDatabaseConnection.h"

class MYPROJECT_API FMyDBManager
{
public:
    FMyDBManager();
    ~FMyDBManager();

    bool Initialize(const FString& DatabasePath);
    void Shutdown();

    bool AddUser(const FString& UserName, int32 Age);
    TArray<FString> GetAllUserNames();

private:
    FSQLiteDatabaseConnection Connection;
    bool bIsInitialized;
};

// 文件: MyDBManager.cpp
#include "MyDBManager.h"
#include "SQLiteResultSet.h"

FMyDBManager::FMyDBManager()
    : bIsInitialized(false)
{
}

FMyDBManager::~FMyDBManager()
{
    Shutdown();
}

bool FMyDBManager::Initialize(const FString& DatabasePath)
{
    if (Connection.Open(*DatabasePath, nullptr, nullptr))
    {
        // 创建表
        Connection.Execute(TEXT(
            "CREATE TABLE IF NOT EXISTS Users ("
            "ID INTEGER PRIMARY KEY AUTOINCREMENT, "
            "UserName TEXT NOT NULL, "
            "Age INTEGER)"
        ));
        bIsInitialized = true;
        return true;
    }
    return false;
}

void FMyDBManager::Shutdown()
{
    if (bIsInitialized)
    {
        Connection.Close();
        bIsInitialized = false;
    }
}

bool FMyDBManager::AddUser(const FString& UserName, int32 Age)
{
    if (!bIsInitialized) return false;

    // 注意：实际应用中应对输入进行转义，防止SQL注入。这里仅为示例。
    FString Query = FString::Printf(TEXT("INSERT INTO Users (UserName, Age) VALUES ('%s', %d)"), *UserName, Age);
    return Connection.Execute(*Query);
}

TArray<FString> FMyDBManager::GetAllUserNames()
{
    TArray<FString> UserNames;
    if (!bIsInitialized) return UserNames;

    FSQLiteResultSet* ResultSet = nullptr;
    Connection.Execute(TEXT("SELECT UserName FROM Users"), ResultSet);

    if (ResultSet && !ResultSet->HasError())
    {
        ResultSet->MoveToFirst();
        while (!ResultSet->IsAtEnd())
        {
            UserNames.Add(ResultSet->GetString(TEXT("UserName")));
            ResultSet->MoveToNext();
        }
        delete ResultSet;
    }
    return UserNames;
}
```

## 模块依赖

该插件依赖于以下核心模块以提供完整的 SQLite 功能。

| 模块 | 用途 |
|---|---|
| `DatabaseSupport` | 提供通用的数据库接口基类 `FDataBaseConnection` 和 `FDataBaseRecordSet`。 |
| `SQLiteCore` | 提供底层的 SQLite C API 封装、预处理语句等核心功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到 UE_LOGF。 |
| 2025-10-31 | `c57f0b00` | Clarified that the output param of Step was only filled for error cases, and not when a row is retur | 澄清了 Step 函数的输出参数仅在错误时填充，而非成功返回行时。 |
| 2025-10-31 | `c8c0f285` | PR #12093: add error detection for SQLiteSupport | 为 SQLiteSupport 添加了错误检测功能。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录结构调整。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为安全协议。 |

### 维护评价

该插件创建于 2019 年初，是一个相对成熟的运行时插件。从提交历史看，它并未处于高度活跃的开发状态，但在 2025 年 10 月仍有针对错误处理和文档注释的改进提交，表明 Epic 仍在对其进行维护和澄清。插件功能稳定，接口变化不大。对于需要本地 SQLite 支持的项目，它仍然是官方提供且可靠的选择，但开发者应注意其 `EnabledByDefault` 为 `false`，需手动在项目中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/SQLiteSupport)
- 官方文档：无
- 测试用例：此插件提供的文件信息中未包含独立的测试文件。