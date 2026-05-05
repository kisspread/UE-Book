# SQLite Support

> SQLite Database Support

| 属性 | 值 |
|---|---|
| 分类 | Database |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | SQLiteSupport (Runtime) |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/SQLiteSupport) | |

## 用途

SQLiteSupport 是 UE5 数据库抽象层的高层封装，为 `FDataBaseConnection` 接口提供了 SQLite 的具体实现。

UE5 的数据库架构分三层：

1. **DatabaseSupport** — 定义了抽象基类 `FDataBaseConnection` 和 `FDataBaseRecordSet`，提供统一的数据库访问接口
2. **SQLiteCore** — 封装原生 SQLite3 C 库，提供 `FSQLiteDatabase`、`FSQLitePreparedStatement` 等底层类
3. **SQLiteSupport（本插件）** — 在 SQLiteCore 之上，实现了 DatabaseSupport 定义的抽象接口

SQLiteSupport 存在的意义是：如果你的代码已经使用了 `FDataBaseConnection` / `FDataBaseRecordSet` 这套抽象接口（例如早期的 UE4 代码），可以直接使用 SQLiteSupport 来获得 SQLite 后端支持，无需改动上层代码。

**但是**，如果你是从零开始写新代码，**推荐直接使用 SQLiteCore**，因为：
- SQLiteCore 的 API 更现代、更完整（支持 prepared statement 绑定、blob、GUID 等）
- SQLiteSupport 的 `FSQLiteResultSet` 在构造时会一次性遍历所有行来计算记录数，性能不如 SQLiteCore 的流式回调 API
- SQLiteSupport 没有自己的测试用例，测试都在 SQLiteCore 中

## 使用场景

- 你有一段遗留代码使用了 `FDataBaseConnection` 接口，需要切换到 SQLite 后端 → 用 SQLiteSupport
- 你需要在 UE5 中使用 SQLite 数据库存储游戏数据 → 直接用 SQLiteCore（更推荐）
- 你需要跨平台的轻量级本地数据库 → SQLiteCore 是最佳选择，SQLiteSupport 是可选的高层封装

## 蓝图用法

本插件没有暴露任何蓝图接口。所有类都是纯 C++ 类，没有 `UCLASS`、`UFUNCTION` 或 `UPROPERTY` 标记。

## C++ 用法

### 头文件引入

```cpp
#include "SQLiteDatabaseConnection.h"
```

### 基本用法 — FSQLiteDatabaseConnection

`FSQLiteDatabaseConnection` 继承自 `FDataBaseConnection`，提供 Open / Close / Execute 三个核心操作。

```cpp
#include "SQLiteDatabaseConnection.h"

// 创建连接
FSQLiteDatabaseConnection Connection;

// 打开数据库文件（ConnectionString 是文件路径）
bool bOpened = Connection.Open(
    TEXT("C:/MyGame/Data/GameData.db"),
    TEXT(""),   // RemoteConnectionIP（SQLite 不使用）
    TEXT("")    // RemoteConnectionStringOverride（SQLite 不使用）
);

// 执行无返回值的 SQL（CREATE / INSERT / UPDATE / DELETE）
bool bSuccess = Connection.Execute(TEXT(
    "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, score INTEGER)"
));
Connection.Execute(TEXT("INSERT INTO players (name, score) VALUES ('Alice', 100)"));

// 执行带返回值的 SQL（SELECT）
FSQLiteResultSet* ResultSet = nullptr;
if (Connection.Execute(TEXT("SELECT * FROM players"), ResultSet))
{
    // 使用 FDataBaseRecordSet::TIterator 遍历结果
    for (FDataBaseRecordSet::TIterator It(ResultSet); It; ++It)
    {
        FString Name = It->GetString(TEXT("name"));
        int32 Score = It->GetInt(TEXT("score"));
        UE_LOG(LogTemp, Log, TEXT("Player: %s, Score: %d"), *Name, Score);
    }
    
    // 用完必须手动释放
    delete ResultSet;
}

// 关闭连接
Connection.Close();
```

### 获取错误信息

```cpp
if (!Connection.Execute(TEXT("INVALID SQL")))
{
    FString Error = Connection.GetLastError();
    UE_LOG(LogTemp, Error, TEXT("SQL Error: %s"), *Error);
}
```

### FSQLiteResultSet 迭代方法

`FSQLiteResultSet` 继承自 `FDataBaseRecordSet`，支持以下数据读取方法：

| 方法 | 返回类型 | 说明 |
|---|---|---|
| `GetString(Column)` | `FString` | 获取字符串列值 |
| `GetInt(Column)` | `int32` | 获取整数列值 |
| `GetFloat(Column)` | `float` | 获取浮点列值 |
| `GetBigInt(Column)` | `int64` | 获取 64 位整数列值 |
| `GetRecordCount()` | `int32` | 获取总记录数 |
| `GetColumnNames()` | `TArray<FDatabaseColumnInfo>` | 获取列名和类型信息 |

也可以直接使用 `MoveToFirst()` / `MoveToNext()` / `IsAtEnd()` 手动遍历：

```cpp
FSQLiteResultSet* ResultSet = nullptr;
Connection.Execute(TEXT("SELECT * FROM players"), ResultSet);

ResultSet->MoveToFirst();
while (!ResultSet->IsAtEnd())
{
    FString Name = ResultSet->GetString(TEXT("name"));
    int32 Score = ResultSet->GetInt(TEXT("score"));
    // ...
    ResultSet->MoveToNext();
}

delete ResultSet;
```

### 进阶用法 — 直接使用 SQLiteCore

对于新项目，推荐直接使用 SQLiteCore 提供的更强大 API：

```cpp
#include "SQLiteDatabase.h"

FSQLiteDatabase Database;
Database.Open(TEXT("/path/to/db.sqlite"), ESQLiteDatabaseOpenMode::ReadWriteCreate);

// 简单执行
Database.Execute(TEXT("CREATE TABLE IF NOT EXISTS items (id INTEGER, name TEXT)"));

// 使用回调遍历结果
Database.Execute(TEXT("SELECT * FROM items"), [](const FSQLitePreparedStatement& Stmt)
{
    int64 Id;
    FString Name;
    Stmt.GetColumnValueByName(TEXT("id"), Id);
    Stmt.GetColumnValueByName(TEXT("name"), Name);
    UE_LOG(LogTemp, Log, TEXT("Item: %lld - %s"), Id, *Name);
    return ESQLitePreparedStatementExecuteRowResult::Continue;
});

// 使用 Prepared Statement 绑定参数
FSQLitePreparedStatement Stmt = Database.PrepareStatement(
    TEXT("INSERT INTO items (id, name) VALUES (?, ?)"));
Stmt.SetBindingValueByIndex(1, (int64)42);
Stmt.SetBindingValueByIndex(2, TEXT("Sword"));
Stmt.Execute();
Stmt.Reset();

// 使用类型安全的 Prepared Statement 宏
SQLITE_PREPARED_STATEMENT(FInsertItem,
    "INSERT INTO items (id, name) VALUES (?id, ?name)",
    SQLITE_PREPARED_STATEMENT_COLUMNS(),
    SQLITE_PREPARED_STATEMENT_BINDINGS(int64, FString)
);

FInsertItem InsertStmt = Database.PrepareStatement<FInsertItem>();
InsertStmt.BindAndExecute(42, TEXT("Shield"));

Database.Close();
```

## Demo 示例

以下是一个完整的最小示例，展示如何用 SQLiteSupport 创建表、插入数据、查询数据：

**MyGame.Build.cs**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "SQLiteSupport"   // 会自动传递依赖 DatabaseSupport 和 SQLiteCore
});
```

**SQLiteDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FSQLiteDemo
{
public:
    static void RunDemo();
};
```

**SQLiteDemo.cpp**
```cpp
#include "SQLiteDemo.h"
#include "SQLiteDatabaseConnection.h"
#include "Misc/Paths.h"

void FSQLiteDemo::RunDemo()
{
    // 构造数据库文件路径（使用 Saved 目录）
    FString DbPath = FPaths::ProjectSavedDir() / TEXT("Demo.db");

    FSQLiteDatabaseConnection Connection;
    if (!Connection.Open(*DbPath, TEXT(""), TEXT("")))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open database: %s"), *Connection.GetLastError());
        return;
    }

    // 建表
    Connection.Execute(TEXT(
        "CREATE TABLE IF NOT EXISTS scores ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  player TEXT NOT NULL,"
        "  score INTEGER DEFAULT 0"
        ")"
    ));

    // 插入数据
    Connection.Execute(TEXT("INSERT INTO scores (player, score) VALUES ('Alice', 9500)"));
    Connection.Execute(TEXT("INSERT INTO scores (player, score) VALUES ('Bob', 8700)"));
    Connection.Execute(TEXT("INSERT INTO scores (player, score) VALUES ('Charlie', 10200)"));

    // 查询数据
    FSQLiteResultSet* ResultSet = nullptr;
    if (Connection.Execute(TEXT("SELECT player, score FROM scores ORDER BY score DESC"), ResultSet))
    {
        UE_LOG(LogTemp, Log, TEXT("=== Leaderboard (%d entries) ==="), ResultSet->GetRecordCount());

        for (FDataBaseRecordSet::TIterator It(ResultSet); It; ++It)
        {
            UE_LOG(LogTemp, Log, TEXT("  %s: %d"),
                *It->GetString(TEXT("player")),
                It->GetInt(TEXT("score")));
        }

        delete ResultSet;
    }

    Connection.Close();
    UE_LOG(LogTemp, Log, TEXT("Demo complete. Database saved to: %s"), *DbPath);
}
```

输出示例：
```
=== Leaderboard (3 entries) ===
  Charlie: 10200
  Alice: 9500
  Bob: 8700
```

## 模块依赖

从 `SQLiteSupport.Build.cs` 的 `PublicDependencyModuleNames` 提取。使用 SQLiteSupport 时，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心模块 |
| `DatabaseSupport` | 数据库抽象基类（`FDataBaseConnection`、`FDataBaseRecordSet`） |
| `SQLiteCore` | SQLite3 C 库封装（`FSQLiteDatabase`、`FSQLitePreparedStatement`） |

此外，插件本身还通过 `.uplugin` 的 `Plugins` 字段声明了对 `DatabaseSupport` 和 `SQLiteCore` 两个插件的依赖。

## 维护状态

### 近期更新

SQLiteSupport 本体最后的实质性更新停留在 2023 年：

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da71ab9` | IWYU includes 清理 | 批量减少头文件包含，非功能性改动 |
| 2022-11-07 | `0a10c21ff628` | Release staging 更新 | 引擎发布分支同步 |
| 2019-12-27 | `360d078ca36a` | Copyright 更新 | 版权年份更新，非功能性 |

其底层依赖 SQLiteCore 在 2025 年仍有活跃更新（链接器修复、头文件目录调整等），说明 SQLite 基础设施仍在维护中。

### 维护评价

- **创建时间**: 2019 年，至今约 7 年
- **SQLiteSupport 本体**: 最后一次功能性更新在 2019 年之前，之后全是编译维护和版权更新
- **SQLiteCore（底层）**: 2025 年仍有活跃维护
- **DatabaseSupport（抽象层）**: 2025 年有小改动

**评价**: SQLiteSupport 本身是一个薄封装层，代码量极少（约 150 行有效代码），功能稳定后不需要频繁更新。但 Epic 显然把开发精力放在了 SQLiteCore 上，SQLiteSupport 更像是一个遗留兼容层。**对于新项目，推荐直接使用 SQLiteCore**。

⚠️ 注意：本插件 `EnabledByDefault: false`，需要在项目设置中手动启用，或在 `.uproject` 中添加依赖。

## 相关链接

- [SQLiteSupport 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/SQLiteSupport)
- [SQLiteCore 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/SQLiteCore)（底层 SQLite 封装，推荐直接使用）
- [DatabaseSupport 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/DatabaseSupport)（数据库抽象基类）
- [SQLiteCore 测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/Database/SQLiteCore/Source/SQLiteCore/Private/Tests/SQLiteTest.cpp)
