import mongoose from 'mongoose';

// Remova o "default" da exportação
export const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGO_URI);
    console.log(`✅ MongoDB conectado: ${conn.connection.host}`);
  } catch (error) {
    console.error(`❌ Erro no MongoDB: ${error.message}`);
    process.exit(1);
  }
};