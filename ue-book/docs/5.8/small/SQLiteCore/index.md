# SQLite Core

> Provides a lightweight C++ wrapper for creating and manipulating SQLite databases. It uses the sqlite C library please refer to Engine/Source/ThirdParty/Licenses/SQLite_v3.47.1.license for license details.

| 属性 | 值 |
|---|---|
| 中文名 | SQLite 轻量数据库 |
| 分类 | Database |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SQLiteCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/SQLiteCore) | |

## 用途

SQLiteCore 为 Unreal Engine 提供了一个轻量级的 SQLite 数据库 C++ 封装层。它对底层 sqlite3 C 库进行了面向对象的包装，让开发者可以用 UE 风格的 C++ 代码来操作 SQLite 数据库，而无需直接调用 C API。

该插件主要服务于引擎内部工具链——从 `SupportedPrograms` 字段可以看出，它被 UnrealMultiUserServer、LiveLinkHub 等多人协作和编辑器服务程序使用。这意味着它是一个**基础设施级别的数据库解决方案**，适合存储配置数据、元数据、会话信息等结构化数据，而非用于游戏运行时的大规模数据存储。

为什么存在：
- UE 内部多个服务工具需要持久化存储，但不需要完整的数据库服务（如 MySQL/PostgreSQL）
- SQLite 是零配置、单文件、嵌入式数据库，非常适合工具类应用
- 提供类型安全的 C++ API，支持 UE 常用类型（FString、FName、FText、FDateTime、FGuid 等）

## 使用场景

- 你需要在编辑器工具或服务器进程中存储结构化配置数据 → 用 SQLiteCore
- 你在开发多人协作工具，需要一个轻量的本地数据库 → 用 SQLiteCore
- 你需要将数据保存到单个文件中，便于分发和备份 → 用 SQLiteCore
- 你在构建 UnrealMultiUserServer / LiveLinkHub 等服务程序 → SQLiteCore 是推荐方案

> ⚠️ **注意**：此插件默认未启用（`EnabledByDefault: false`），需要在你的 `.uproject` 或 `.uplugin` 中手动启用。该插件**不包含蓝图接口**，纯 C++ API。

## 蓝图用法

**此插件不提供任何蓝图接口。**

SQLiteCore 的所有头文件中均未声明 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。这是一个纯 C++ 代码库，仅供 C++ 模块使用。

## C++ 用法

### 头文件引入

```cpp
#include "SQLiteDatabase.h"
#include "SQLitePreparedStatement.h"
#include "SQLiteTypes.h"
```

### 基本用法

以下示例展示了打开数据库、执行简单 SQL 语句和查询数据的基本流程。

```cpp
// 打开或创建一个 SQLite 数据库
FSQLiteDatabase Database;
bool bSuccess = Database.Open(
    *FPaths::ProjectSavedDir() / TEXT("MyData.db"),
    ESQLiteDatabaseOpenMode::ReadWriteCreate
);

if (bSuccess)
{
    // 创建表
    Database.Execute(TEXT(
        "CREATE TABLE IF NOT EXISTS Players ("
        "  Id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  Name TEXT NOT NULL,"
        "  Score INTEGER DEFAULT 0"
        ")"
    ));

    // 插入数据
    Database.Execute(TEXT(
        "INSERT INTO Players (Name, Score) VALUES ('Alice', 100)"
    ));

    // 查询数据并枚举行
    int32 RowCount = Database.Execute(TEXT("SELECT Id, Name, Score FROM Players"),
        [&Database](const FSQLitePreparedStatement& Statement) -> ESQLitePreparedStatementExecuteRowResult
        {
            int64 Id;
            FString Name;
            int32 Score;

            Statement.GetColumnValueByName(TEXT("Id"), Id);
            Statement.GetColumnValueByName(TEXT("Name"), Name);
            Statement.GetColumnValueByName(TEXT("Score"), Score);

            UE_LOG(LogTemp, Log, TEXT("Player: %s (ID: %lld, Score: %d)"), *Name, Id, Score);

            return ESQLitePreparedStatementExecuteRowResult::Continue;
        }
    );

    // 关闭数据库
    Database.Close();
}
```

### 预处理语句（Prepared Statement）

预处理语句适合需要重复执行或使用参数绑定的场景，可以避免 SQL 注入并提升性能。

```cpp
FSQLiteDatabase Database;
Database.Open(*FPaths::ProjectSavedDir() / TEXT("MyData.db"));

// 创建预处理语句用于插入数据
FSQLitePreparedStatement InsertStmt;
InsertStmt.Create(Database, TEXT("INSERT INTO Players (Name, Score) VALUES (?, ?)"));

// 使用索引绑定参数（从 1 开始）
InsertStmt.SetBindingValueByIndex(1, TEXT("Bob"));
InsertStmt.SetBindingValueByIndex(2, 250);
InsertStmt.Execute();
InsertStmt.Reset();  // 重置以便再次使用

// 使用名称绑定参数（对应 SQL 中的 :name, @name, $name）
FSQLitePreparedStatement QueryStmt;
QueryStmt.Create(Database, TEXT("SELECT * FROM Players WHERE Score > :MinScore"));
QueryStmt.SetBindingValueByName(TEXT(":MinScore"), 100);

int64 NumRows = QueryStmt.Execute(
    [](const FSQLitePreparedStatement& Statement) -> ESQLitePreparedStatementExecuteRowResult
    {
        FString Name;
        int32 Score;
        Statement.GetColumnValueByName(TEXT("Name"), Name);
        Statement.GetColumnValueByName(TEXT("Score"), Score);
        UE_LOG(LogTemp, Log, TEXT("Found: %s = %d"), *Name, Score);
        return ESQLitePreparedStatementExecuteRowResult::Continue;
    }
);

QueryStmt.Destroy();
InsertStmt.Destroy();
Database.Close();
```

### 进阶用法

#### 使用类型安全的宏定义预处理语句

SQLiteCore 提供了一套模板宏系统，可以在编译期确保绑定参数和列获取的类型安全：

```cpp
// 定义类型安全的预处理语句类型
SQLITE_PREPARED_STATEMENT(
    FMyInsertStatement,
    "INSERT INTO Players (Name, Score) VALUES (?, ?)",
    SQLITE_PREPARED_STATEMENT_COLUMNS(),                              // 无返回列
    SQLITE_PREPARED_STATEMENT_BINDINGS(FString, int32)                // 绑定类型
);

SQLITE_PREPARED_STATEMENT(
    FMyQueryStatement,
    "SELECT Name, Score FROM Players WHERE Score > ?",
    SQLITE_PREPARED_STATEMENT_COLUMNS(FString, int32),                // 返回列类型
    SQLITE_PREPARED_STATEMENT_BINDINGS(int32)                         // 绑定类型
);

// 使用
FSQLiteDatabase Database;
Database.Open(*FPaths::ProjectSavedDir() / TEXT("MyData.db"));

// 类型安全的插入
FMyInsertStatement InsertStmt(Database, ESQLitePreparedStatementFlags::None);
InsertStmt.BindAndExecute(TEXT("Charlie"), 500);  // 编译期类型检查！

// 类型安全的查询
FMyQueryStatement QueryStmt(Database, ESQLitePreparedStatementFlags::None);
FString Name;
int32 Score;
QueryStmt.BindAndExecute(100, [&](const FMyQueryStatement& Stmt) -> ESQLitePreparedStatementExecuteRowResult
{
    Stmt.GetColumnValues(Name, Score);  // 编译期类型安全！
    UE_LOG(LogTemp, Log, TEXT("%s: %d"), *Name, Score);
    return ESQLitePreparedStatementExecuteRowResult::Continue;
});

// 单行查询快捷方式
QueryStmt.BindAndExecuteSingle(200, Name, Score);

Database.Close();
```

#### 处理 BLOB 和 GUID 数据

```cpp
FSQLitePreparedStatement Stmt;
Stmt.Create(Database, TEXT("INSERT INTO Data (Id, Payload) VALUES (?, ?)"));

FGuid MyGuid = FGuid::NewGuid();
TArray<uint8> BlobData;
BlobData.Append(TEXT("Hello Binary"), 12);

Stmt.SetBindingValueByIndex(1, MyGuid);       // GUID 自动序列化为 16 字节 BLOB
Stmt.SetBindingValueByIndex(2, BlobData);      // BLOB 数据
Stmt.Execute();

// 读取时
FGuid ReadGuid;
TArray<uint8> ReadBlob;
Stmt.GetColumnValueByName(TEXT("Id"), ReadGuid);
Stmt.GetColumnValueByName(TEXT("Payload"), ReadBlob);
```

#### 数据库元信息与完整性检查

```cpp
FSQLiteDatabase Database;
Database.Open(TEXT("MyData.db"));

// 设置用户版本（可用于数据库迁移）
Database.SetUserVersion(2);

// 读取用户版本
int32 Version;
Database.GetUserVersion(Version);

// 获取最后插入的行 ID（自增主键）
int64 LastId = Database.GetLastInsertRowId();

// 快速完整性检查
bool bOk = Database.PerformQuickIntegrityCheck();

// 获取错误信息
if (!bOk)
{
    FString LastError = Database.GetLastError();
    UE_LOG(LogTemp, Error, TEXT("Database integrity issue: %s"), *LastError);
}

Database.Close();
```

## Demo 示例

一个完整的、可编译的最小示例，演示 SQLiteCore 的基本 CRUD 操作：

```cpp
// SQLiteDemo.h
#pragma once

#include "CoreMinimal.h"
#include "SQLiteDatabase.h"
#include "SQLitePreparedStatement.h"

class FSQLiteDemo
{
public:
    /** 初始化数据库并创建表 */
    static bool InitializeDatabase(const FString& DbPath, FSQLiteDatabase& OutDatabase);

    /** 插入一条记录 */
    static bool InsertRecord(FSQLiteDatabase& Database, const FString& Name, int32 Score);

    /** 查询所有记录 */
    static void QueryAllRecords(FSQLiteDatabase& Database);

    /** 按分数查询记录 */
    static void QueryByMinScore(FSQLiteDatabase& Database, int32 MinScore);
};
```

```cpp
// SQLiteDemo.cpp
#include "SQLiteDemo.h"
#include "Misc/Paths.h"

bool FSQLiteDemo::InitializeDatabase(const FString& DbPath, FSQLiteDatabase& OutDatabase)
{
    if (!OutDatabase.Open(*DbPath, ESQLiteDatabaseOpenMode::ReadWriteCreate))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open database: %s"), *DbPath);
        return false;
    }

    // 创建示例表
    const TCHAR* CreateTableSQL = TEXT(
        "CREATE TABLE IF NOT EXISTS Scores ("
        "  Id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  Name TEXT NOT NULL,"
        "  Score INTEGER NOT NULL DEFAULT 0,"
        "  CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP"
        ")"
    );

    if (!OutDatabase.Execute(CreateTableSQL))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create table: %s"), *OutDatabase.GetLastError());
        return false;
    }

    // 设置数据库用户版本
    OutDatabase.SetUserVersion(1);

    return true;
}

bool FSQLiteDemo::InsertRecord(FSQLiteDatabase& Database, const FString& Name, int32 Score)
{
    FSQLitePreparedStatement Statement;
    Statement.Create(Database, TEXT("INSERT INTO Scores (Name, Score) VALUES (?, ?)"));

    Statement.SetBindingValueByIndex(1, Name);
    Statement.SetBindingValueByIndex(2, Score);

    bool bResult = Statement.Execute();
    Statement.Destroy();

    return bResult;
}

void FSQLiteDemo::QueryAllRecords(FSQLiteDatabase& Database)
{
    UE_LOG(LogTemp, Log, TEXT("=== All Records ==="));

    int32 Count = 0;
    Database.Execute(TEXT("SELECT Id, Name, Score FROM Scores"),
        [&Count](const FSQLitePreparedStatement& Statement) -> ESQLitePreparedStatementExecuteRowResult
        {
            int64 Id;
            FString Name;
            int32 Score;

            Statement.GetColumnValueByName(TEXT("Id"), Id);
            Statement.GetColumnValueByName(TEXT("Name"), Name);
            Statement.GetColumnValueByName(TEXT("Score"), Score);

            UE_LOG(LogTemp, Log, TEXT("  [%lld] %s = %d"), Id, *Name, Score);
            Count++;

            return ESQLitePreparedStatementExecuteRowResult::Continue;
        }
    );

    UE_LOG(LogTemp, Log, TEXT("Total: %d records"), Count);
}

void FSQLiteDemo::QueryByMinScore(FSQLiteDatabase& Database, int32 MinScore)
{
    UE_LOG(LogTemp, Log, TEXT("=== Records with Score > %d ==="), MinScore);

    // 使用预处理语句避免 SQL 注入
    FSQLitePreparedStatement Statement;
    Statement.Create(Database, TEXT("SELECT Id, Name, Score FROM Scores WHERE Score > :MinScore"));
    Statement.SetBindingValueByName(TEXT(":MinScore"), MinScore);

    Statement.Execute([&Statement](const FSQLitePreparedStatement& InStmt) -> ESQLitePreparedStatementExecuteRowResult
    {
        FString Name;
        int32 Score;
        InStmt.GetColumnValueByName(TEXT("Name"), Name);
        InStmt.GetColumnValueByName(TEXT("Score"), Score);

        UE_LOG(LogTemp, Log, TEXT("  %s: %d"), *Name, Score);
        return ESQLitePreparedStatementExecuteRowResult::Continue;
    });

    Statement.Destroy();
}
```

**调用示例：**

```cpp
FSQLiteDatabase Database;
FString DbPath = FPaths::ProjectSavedDir() / TEXT("DemoScores.db");

if (FSQLiteDemo::InitializeDatabase(DbPath, Database))
{
    FSQLiteDemo::InsertRecord(Database, TEXT("Alice"), 100);
    FSQLiteDemo::InsertRecord(Database, TEXT("Bob"), 250);
    FSQLiteDemo::InsertRecord(Database, TEXT("Charlie"), 500);

    FSQLiteDemo::QueryAllRecords(Database);
    FSQLiteDemo::QueryByMinScore(Database, 150);

    Database.Close();
}
```

## 模块依赖

SQLiteCore 的构建依赖主要围绕引擎核心和 SQLite 第三方库。根据插件结构分析：

| 模块 | 用途 |
|---|---|
| `SQLite` | 底层 SQLite C 库的 ThirdParty 模块封装 |

无特殊依赖（仅标准 Core/Engine 等基础模块）。插件通过 `#include "IncludeSQLite.h"` 引入 sqlite3.h，实际的 sqlite3 C 源码位于 `Engine/Source/ThirdParty/SQLite/` 下。

要在你的 Build.cs 中使用 SQLiteCore：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "SQLiteCore"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `d1f697a8` | [Backout] - CL53616706 | 回退了一个之前的改动 |
| 2026-05-12 | `92e8cec9` | UnrealBuildTool: Enable CastFunctionTypeMismatchWarningLevel as error by default in the build setting | 构建系统调整，将类型转换警告提升为错误 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 新宏 |
| 2025-10-31 | `6f21cd1e` | Fixed comment | 修复注释内容 |
| 2025-10-31 | `c57f0b00` | Clarified that the output param of Step was only filled for error cases, and not when a row is returned | 澄清 Step 函数的输出参数仅在错误时填充，返回行时不填充 |

### 维护评价

**维护中** — SQLiteCore 仍处于活跃维护状态。

- **年龄**：约 7 年（2019 年创建），属于老古董级别但仍在维护
- **更新频率**：最近 1 年内有多次提交，包含文档改进（注释修复）、构建系统适配和日志宏迁移
- **功能性更新**：近期更新主要是工程层面的维护（构建配置、日志迁移、注释改进），无重大功能变更
- **底层 SQLite 版本**：使用 SQLite 3.47.1（2024 年 11 月发布），版本较新
- **内部使用**：作为 Epic 内部多人服务器和 LiveLinkHub 等工具的基础设施，不太可能被废弃
- **限制**：默认未启用，仅支持特定程序（SupportedPrograms）；无蓝图支持；无 Content 包含

✅ **推荐使用**，特别是构建编辑器工具或服务器程序时。作为底层基础设施插件，它设计稳定，API 简洁清晰，且有 Epic 内部工具作为长期使用者。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/SQLiteCore)
- [SQLite 官方文档](https://www.sqlite.org/docs.html)（底层 C 库文档）
- [SQLite 许可证](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Source/ThirdParty/Licenses/SQLite_v3.47.1.license)