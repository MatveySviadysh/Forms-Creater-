import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './styles.module.css';

type QuestionType = 'text' | 'radio' | 'checkbox' | 'dropdown' | 'linear_scale';

interface QuestionOption {
  id: string;
  value: string;
}

interface FormQuestion {
  question_id: string;
  title: string;
  type: QuestionType;
  required: boolean;
  options?: QuestionOption[];
  min_value?: number;
  max_value?: number;
  min_label?: string;
  max_label?: string;
}

interface Form {
  id: number;
  title: string;
  description: string;
  created_at: string;
}

const CreateForm: React.FC = () => {
  const navigate = useNavigate();
  const [formTitle, setFormTitle] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [questions, setQuestions] = useState<FormQuestion[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [forms, setForms] = useState<Form[]>([]);
  const [showForms, setShowForms] = useState(false);
  const [loadingForms, setLoadingForms] = useState(false);

  // Загрузка всех форм
  const fetchForms = async () => {
    setLoadingForms(true);
    setError(null);
    try {
      const response = await fetch('http://localhost/api/forms/forms/forms/');
      if (!response.ok) {
        throw new Error('Ошибка при загрузке форм');
      }
      const data = await response.json();
      setForms(data);
      setShowForms(!showForms);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
      console.error('Ошибка загрузки форм:', err);
    } finally {
      setLoadingForms(false);
    }
  };

  const addQuestion = () => {
    setQuestions([
      ...questions,
      {
        question_id: Date.now().toString(),
        title: '',
        type: 'text',
        required: false,
        options: []
      }
    ]);
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const updateQuestion = (index: number, field: keyof FormQuestion, value: any) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index] = {
      ...updatedQuestions[index],
      [field]: value
    };
    setQuestions(updatedQuestions);
  };

  const addOption = (questionIndex: number) => {
    const updatedQuestions = [...questions];
    updatedQuestions[questionIndex].options = [
      ...(updatedQuestions[questionIndex].options || []),
      { id: Date.now().toString(), value: '' }
    ];
    setQuestions(updatedQuestions);
  };

  const removeOption = (questionIndex: number, optionIndex: number) => {
    const updatedQuestions = [...questions];
    updatedQuestions[questionIndex].options = 
      updatedQuestions[questionIndex].options?.filter((_, i) => i !== optionIndex);
    setQuestions(updatedQuestions);
  };

  const updateOption = (questionIndex: number, optionIndex: number, value: string) => {
    const updatedQuestions = [...questions];
    if (updatedQuestions[questionIndex].options) {
      updatedQuestions[questionIndex].options![optionIndex].value = value;
      setQuestions(updatedQuestions);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsSubmitting(true);
  setError(null);

  try {
    // Подготовка данных в точном соответствии с ожидаемой структурой
    const requestData = {
      title: formTitle,
      description: formDescription,
      questions: questions.map(question => ({
        id: question.question_id,  // Используем question_id как id
        title: question.title,
        type: question.type,
        required: question.required,
        options: question.type === 'text' ? undefined : question.options?.map(opt => ({
          id: opt.id,
          value: opt.value
        })),
        min_value: question.type === 'linear_scale' ? question.min_value : undefined,
        max_value: question.type === 'linear_scale' ? question.max_value : undefined,
        min_label: question.type === 'linear_scale' ? question.min_label : undefined,
        max_label: question.type === 'linear_scale' ? question.max_label : undefined
      }))
    };

    console.log('Отправляемые данные:', JSON.stringify(requestData, null, 2));

    const response = await fetch('http://localhost/api/forms/forms/forms/', {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });

    const data = await response.json();

    if (!response.ok) {
      // Улучшенная обработка ошибок
      let errorMessage = 'Ошибка при создании формы';
      if (data.detail) {
        errorMessage = typeof data.detail === 'string' 
          ? data.detail
          : JSON.stringify(data.detail);
      }
      throw new Error(errorMessage);
    }

    alert(`Форма успешно создана! ID: ${data.id}`);
    navigate('/');
  } catch (error) {
    console.error('Ошибка:', error);
    setError(error instanceof Error ? error.message : 'Неизвестная ошибка');
  } finally {
    setIsSubmitting(false);
  }
};

  return (
    <div className={styles.container}>
      <h1>Создание новой формы</h1>
      
      <button 
        onClick={fetchForms}
        className={styles.showFormsButton}
        disabled={loadingForms}
      >
        {loadingForms ? 'Загрузка...' : (showForms ? 'Скрыть формы' : 'Показать все формы')}
      </button>

      {showForms && (
        <div className={styles.formsList}>
          <h2>Мои формы</h2>
          {forms.length === 0 ? (
            <p>Нет созданных форм</p>
          ) : (
            <ul>
              {forms.map(form => (
                <li key={form.id} className={styles.formItem}>
                  <h3>{form.title}</h3>
                  <p>{form.description}</p>
                  <small>Создано: {new Date(form.created_at).toLocaleString()}</small>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {error && <div className={styles.error}>{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label>Название формы:</label>
          <input
            type="text"
            value={formTitle}
            onChange={(e) => setFormTitle(e.target.value)}
            required
            disabled={isSubmitting}
          />
        </div>

        <div className={styles.formGroup}>
          <label>Описание формы:</label>
          <textarea
            value={formDescription}
            onChange={(e) => setFormDescription(e.target.value)}
            disabled={isSubmitting}
          />
        </div>

        <div className={styles.questions}>
          {questions.map((question, qIndex) => (
            <div key={question.question_id} className={styles.question}>
              <h3>Вопрос {qIndex + 1}</h3>
              
              <div className={styles.formGroup}>
                <label>Текст вопроса:</label>
                <input
                  type="text"
                  value={question.title}
                  onChange={(e) => updateQuestion(qIndex, 'title', e.target.value)}
                  required
                  disabled={isSubmitting}
                />
              </div>
              
              <div className={styles.formGroup}>
                <label>Тип вопроса:</label>
                <select
                  value={question.type}
                  onChange={(e) => updateQuestion(qIndex, 'type', e.target.value as QuestionType)}
                  disabled={isSubmitting}
                >
                  <option value="text">Текстовый ответ</option>
                  <option value="radio">Один вариант</option>
                  <option value="checkbox">Несколько вариантов</option>
                  <option value="dropdown">Выпадающий список</option>
                  <option value="linear_scale">Линейная шкала</option>
                </select>
              </div>
              
              <div className={styles.formGroup}>
                <label>
                  <input
                    type="checkbox"
                    checked={question.required}
                    onChange={(e) => updateQuestion(qIndex, 'required', e.target.checked)}
                    disabled={isSubmitting}
                  />
                  Обязательный вопрос
                </label>
              </div>
              
              {question.type === 'linear_scale' && (
                <>
                  <div className={styles.formGroup}>
                    <label>Минимальное значение:</label>
                    <input
                      type="number"
                      value={question.min_value || 1}
                      onChange={(e) => updateQuestion(qIndex, 'min_value', parseInt(e.target.value))}
                      disabled={isSubmitting}
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label>Максимальное значение:</label>
                    <input
                      type="number"
                      value={question.max_value || 5}
                      onChange={(e) => updateQuestion(qIndex, 'max_value', parseInt(e.target.value))}
                      disabled={isSubmitting}
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label>Подпись минимума:</label>
                    <input
                      type="text"
                      value={question.min_label || ''}
                      onChange={(e) => updateQuestion(qIndex, 'min_label', e.target.value)}
                      disabled={isSubmitting}
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label>Подпись максимума:</label>
                    <input
                      type="text"
                      value={question.max_label || ''}
                      onChange={(e) => updateQuestion(qIndex, 'max_label', e.target.value)}
                      disabled={isSubmitting}
                    />
                  </div>
                </>
              )}
              
              {(question.type === 'radio' || question.type === 'checkbox' || question.type === 'dropdown') && (
                <div className={styles.options}>
                  <h4>Варианты ответов:</h4>
                  {question.options?.map((option, oIndex) => (
                    <div key={option.id} className={styles.option}>
                      <input
                        type="text"
                        value={option.value}
                        onChange={(e) => updateOption(qIndex, oIndex, e.target.value)}
                        placeholder="Текст варианта"
                        disabled={isSubmitting}
                      />
                      <button
                        type="button"
                        onClick={() => removeOption(qIndex, oIndex)}
                        className={styles.removeButton}
                        disabled={isSubmitting}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={() => addOption(qIndex)}
                    className={styles.addButton}
                    disabled={isSubmitting}
                  >
                    + Добавить вариант
                  </button>
                </div>
              )}
              
              <button
                type="button"
                onClick={() => removeQuestion(qIndex)}
                className={styles.removeQuestionButton}
                disabled={isSubmitting}
              >
                Удалить вопрос
              </button>
            </div>
          ))}
        </div>

        <div className={styles.buttons}>
          <button 
            type="button" 
            onClick={addQuestion} 
            className={styles.addButton}
            disabled={isSubmitting}
          >
            Добавить вопрос
          </button>
          <button 
            type="submit" 
            className={styles.submitButton}
            disabled={isSubmitting || questions.length === 0}
          >
            {isSubmitting ? 'Сохранение...' : 'Сохранить форму'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateForm;