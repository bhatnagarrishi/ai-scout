import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import neo4j, { Driver, Session, Result } from 'neo4j-driver';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class Neo4jService implements OnModuleInit, OnModuleDestroy {
    private driver: Driver;

    constructor(private configService: ConfigService) { }

    async onModuleInit() {
        const uri = this.configService.get<string>('NEO4J_URI') || 'bolt://localhost:7687';
        const username = this.configService.get<string>('NEO4J_USERNAME') || 'neo4j';
        const password = this.configService.get<string>('NEO4J_PASSWORD') || 'password';

        this.driver = neo4j.driver(uri, neo4j.auth.basic(username, password));

        // Verify connection
        try {
            await this.driver.verifyConnectivity();
            console.log('Connected to Neo4j');
        } catch (error) {
            console.error('Could not connect to Neo4j', error);
        }
    }

    async onModuleDestroy() {
        if (this.driver) {
            await this.driver.close();
        }
    }

    getDriver(): Driver {
        return this.driver;
    }

    getReadSession(database?: string): Session {
        return this.driver.session({
            database: database || 'neo4j',
            defaultAccessMode: neo4j.session.READ,
        });
    }

    getWriteSession(database?: string): Session {
        return this.driver.session({
            database: database || 'neo4j',
            defaultAccessMode: neo4j.session.WRITE,
        });
    }

    async read(cypher: string, params: Record<string, any> = {}, database?: string): Promise<Result> {
        const session = this.getReadSession(database);
        try {
            return await session.run(cypher, params);
        } finally {
            await session.close();
        }
    }

    async write(cypher: string, params: Record<string, any> = {}, database?: string): Promise<Result> {
        const session = this.getWriteSession(database);
        try {
            return await session.run(cypher, params);
        } finally {
            await session.close();
        }
    }
}
